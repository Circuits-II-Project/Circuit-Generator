import unittest

from formula_input_test import (
    has_valid_time_interval,
    number_matches_rule,
    parse_finite_number,
    parse_positive_list,
)


# Estas pruebas revisan las conversiones antes de que el programa pida datos en consola.
class FormulaInputValidationTests(unittest.TestCase):
    def test_valid_finite_scalar_is_converted_to_float(self) -> None:
        self.assertEqual(parse_finite_number("-12.5"), -12.5)

    def test_invalid_text_and_empty_input_are_rejected(self) -> None:
        for value in ("not a number", ""):
            with self.subTest(value=value):
                self.assertIsNone(parse_finite_number(value))

    def test_nan_and_infinity_are_rejected(self) -> None:
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                self.assertIsNone(parse_finite_number(value))

    def test_positive_rule_rejects_zero_and_negative_values(self) -> None:
        for value in (0.0, -1.0):
            with self.subTest(value=value):
                self.assertFalse(number_matches_rule(value, "positive"))

    def test_signed_rule_accepts_negative_values(self) -> None:
        self.assertTrue(number_matches_rule(-1.0, "signed"))

    def test_valid_comma_separated_list_is_converted(self) -> None:
        self.assertEqual(parse_positive_list("1, 2.5, 3"), [1.0, 2.5, 3.0])

    def test_list_with_invalid_text_or_empty_item_is_rejected(self) -> None:
        for value in ("1, no", "1, , 3"):
            with self.subTest(value=value):
                self.assertIsNone(parse_positive_list(value))

    def test_positive_list_rejects_zero_and_negative_values(self) -> None:
        for value in ("1, 0, 3", "1, -2, 3"):
            with self.subTest(value=value):
                self.assertIsNone(parse_positive_list(value))

    def test_non_negative_and_signed_rules_handle_boundary_values(self) -> None:
        self.assertFalse(number_matches_rule(-1.0, "non_negative"))
        self.assertTrue(number_matches_rule(0.0, "non_negative"))
        self.assertTrue(number_matches_rule(-90.0, "signed"))

    def test_source_frequency_zero_is_rejected(self) -> None:
        self.assertFalse(number_matches_rule(0.0, "positive"))

    def test_time_must_be_greater_than_previous_time(self) -> None:
        self.assertTrue(has_valid_time_interval(1.0, 1.5))
        self.assertFalse(has_valid_time_interval(1.0, 1.0))
        self.assertFalse(has_valid_time_interval(1.0, 0.5))


if __name__ == "__main__":
    unittest.main()
