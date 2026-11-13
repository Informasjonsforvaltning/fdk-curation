import os
import tempfile
import unittest
import urllib.error
from unittest import mock

import validate_high_value_dataset_types as validator

HEADER = "fdkId,title,eu-hvd,national-hvd,national-basic-data\n"
FDK_ID = "d40dbd5f-58f5-3a1c-96bc-8ecc2d712422"
OTHER_FDK_ID = "00000000-0000-0000-0000-000000000000"


def http_error(code):
    return urllib.error.HTTPError(validator.DATASET_API, code, "error", {}, None)


class ValidateTest(unittest.TestCase):
    def validate(self, content, check_exists=False):
        with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8", delete=False) as file:
            file.write(content)
        self.addCleanup(os.remove, file.name)
        return validator.validate(file.name, check_exists)

    def test_valid_file(self):
        content = HEADER + f'{FDK_ID},"Tittel, med komma",ja,nei,Nei\n'
        self.assertEqual([], self.validate(content))

    def test_only_header(self):
        self.assertEqual([], self.validate(HEADER))

    def test_byte_order_mark_and_empty_lines(self):
        content = "﻿" + HEADER + "\n" + f"{FDK_ID},Tittel,ja,nei,nei\n"
        self.assertEqual([], self.validate(content))

    def test_wrong_header(self):
        errors = self.validate("fdkId;title;eu-hvd;national-hvd;national-basic-data\n")
        self.assertEqual(1, len(errors))
        self.assertIn("Linje 1", errors[0])

    def test_empty_file(self):
        self.assertIn("(tom fil)", self.validate("")[0])

    def test_wrong_number_of_columns(self):
        errors = self.validate(HEADER + f"{FDK_ID},Tittel, med komma,ja,nei,nei\n")
        self.assertEqual(["Linje 2: forventet 5 kolonner, fant 6. Husk anførselstegn rundt titler med komma"], errors)

    def test_invalid_fdk_id(self):
        errors = self.validate(HEADER + "abc,Tittel,ja,nei,nei\n")
        self.assertEqual(["Linje 2: «abc» er ikke en gyldig fdkId"], errors)

    def test_duplicate_fdk_id(self):
        errors = self.validate(HEADER + f"{FDK_ID},A,ja,nei,nei\n{FDK_ID},B,nei,ja,nei\n")
        self.assertEqual([f"Linje 3: fdkId {FDK_ID} finnes allerede på linje 2"], errors)

    def test_invalid_value(self):
        errors = self.validate(HEADER + f"{FDK_ID},Tittel,x,nei,\n")
        self.assertEqual(
            [
                "Linje 2: «eu-hvd» må være ja eller nei, fant «x»",
                "Linje 2: «national-basic-data» må være ja eller nei, fant «»",
            ],
            errors,
        )

    def test_dataset_not_found(self):
        content = HEADER + f"{FDK_ID},A,ja,nei,nei\n{OTHER_FDK_ID},B,ja,nei,nei\n"
        with mock.patch.object(validator, "dataset_exists", side_effect=lambda fdk_id: fdk_id == FDK_ID):
            errors = self.validate(content, check_exists=True)
        self.assertEqual([f"Linje 3: fant ikke datasett med fdkId {OTHER_FDK_ID} på data.norge.no"], errors)


class DatasetExistsTest(unittest.TestCase):
    def setUp(self):
        sleep = mock.patch.object(validator.time, "sleep")
        self.sleep = sleep.start()
        self.addCleanup(sleep.stop)

    def response(self, status):
        response = mock.MagicMock()
        response.__enter__.return_value.status = status
        return response

    def test_found(self):
        with mock.patch.object(validator.urllib.request, "urlopen", return_value=self.response(200)):
            self.assertTrue(validator.dataset_exists(FDK_ID))

    def test_not_found_is_not_retried(self):
        with mock.patch.object(validator.urllib.request, "urlopen", side_effect=http_error(404)) as urlopen:
            self.assertFalse(validator.dataset_exists(FDK_ID))
        self.assertEqual(1, urlopen.call_count)

    def test_retries_on_server_error(self):
        side_effect = [http_error(503), urllib.error.URLError("timeout"), self.response(200)]
        with mock.patch.object(validator.urllib.request, "urlopen", side_effect=side_effect) as urlopen:
            self.assertTrue(validator.dataset_exists(FDK_ID))
        self.assertEqual(3, urlopen.call_count)
        self.assertEqual(2, self.sleep.call_count)

    def test_raises_after_last_attempt(self):
        with mock.patch.object(validator.urllib.request, "urlopen", side_effect=http_error(503)) as urlopen:
            with self.assertRaises(urllib.error.HTTPError):
                validator.dataset_exists(FDK_ID)
        self.assertEqual(validator.ATTEMPTS, urlopen.call_count)


if __name__ == "__main__":
    unittest.main()
