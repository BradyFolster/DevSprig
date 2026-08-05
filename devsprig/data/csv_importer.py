#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Google Forms response CSV files and indentify question types.

Responsibilities of this file:
    1. Confirm that the selected file exists
    2. Confirm that it is a CSV file
    3. Load the CSV into a pandas DataFrame
    4. Preserve the original response values
    5. Identify the analysis type of each column
    6. Return the DataFrame and question information

NO CALCULATIONS ARE DONE IN HERE
"""

# Path is easier to use cross-platform
from pathlib import Path

# re provides regular-expression tools
import re

# pandas loads and stores the csv as a table called a DataFrame
import pandas as pd

# Specific errors that pandas may raise
from pandas.errors import EmptyDataError, ParserError

# Import the question models defined in question.py
from devsprig.models.question import(
    DetectionConfidence,
    QuestionInfo,
    QuestionType    
)


class CsvImportError(Exception):
    # Represents a problem preventing DevSprig from importing a csv

def normalize_header(header: str) -> str:
    # Makes all "variations" of upper/lowercase and spaces consistent
    
    normalized = header.lower()
    
    #Replace anything other than letters or numbers with spaces
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    
    # Split on whitespace and join the pieces with one space
    normalized = " ".join(normalized.split())
    
    return normalized

# Dictionary shows the exact questions in the DevSprig Google Forms Template
# Each value contains: question type, min/max scale value, whether higher values are better
OFFICIAL_TEMPLATE_QUESTIONS: dict[
    str,
    tuple[QuestionType, int | None, int | None, bool | None],
] = {
    normalize_header(
        "Timestamp"
    ): (
        QuestionType.TIMESTAMP,
        None,
        None,
        None,
    ),

    normalize_header(
        "Enter your participant ID."
    ): (
        QuestionType.IDENTIFIER,
        None,
        None,
        None,
    ),

    normalize_header(
        "Which version of the product did you test?"
    ): (
        QuestionType.CATEGORY,
        None,
        None,
        None,
    ),

    normalize_header(
        "Which device or platform did you use?"
    ): (
        QuestionType.CATEGORY,
        None,
        None,
        None,
    ),

    normalize_header(
        "How familiar were you with similar products before this test?"
    ): (
        QuestionType.RATING_SCALE,
        1,
        5,
        True,
    ),

    normalize_header(
        "Were you able to complete the assigned task?"
    ): (
        QuestionType.TASK_COMPLETION,
        None,
        None,
        None,
    ),

    normalize_header(
        "How easy or difficult was the task?"
    ): (
        QuestionType.RATING_SCALE,
        1,
        5,
        True,
    ),

    normalize_header(
        "How confident are you that you completed it correctly?"
    ): (
        QuestionType.RATING_SCALE,
        1,
        5,
        True,
    ),

    normalize_header(
        "Approximately how long did the task take? (minutes)"
    ): (
        QuestionType.DURATION,
        None,
        None,
        None,
    ),

    normalize_header(
        "Which problems did you experience?"
    ): (
        QuestionType.CHECKBOXES,
        None,
        None,
        None,
    ),

    normalize_header(
        "Overall, how satisfied were you with the product?"
    ): (
        QuestionType.RATING_SCALE,
        1,
        5,
        True,
    ),

    normalize_header(
        "What part of the experience was most useful or enjoyable?"
    ): (
        QuestionType.WRITTEN_RESPONSE,
        None,
        None,
        None,
    ),

    normalize_header(
        "What part was most confusing or frustrating?"
    ): (
        QuestionType.WRITTEN_RESPONSE,
        None,
        None,
        None,
    ),

    normalize_header(
        "What is the single most important change you would make?"
    ): (
        QuestionType.WRITTEN_RESPONSE,
        None,
        None,
        None,
    ),

    normalize_header(
        "How likely are you to recommend this product "
        "to a friend or colleague?"
    ): (
        QuestionType.NPS,
        0,
        10,
        True,
    ),

    normalize_header(
        "Is there anything else you would like to tell us?"
    ): (
        QuestionType.WRITTEN_RESPONSE,
        None,
        None,
        None,
    ),

    # Keep the original misspelled version as an alias so old development
    # CSV files can still be imported successfully.
    normalize_header(
        "How likely are you to recommend this product "
        "to a friend or collague?"
    ): (
        QuestionType.NPS,
        0,
        10,
        True,
    ),
}
        
def load_csv(file_path: str | Path,) -> tuple[pd.DataFrame, list[QuestionInfo]]:
    """
    Load a Google Forms response CSV and identify its columns.
    
    Takes file_path 
    Returns tuple (DataFrame, list[QuestionInfo])
    Raises CsvImportError when the file is missing, not vsc, empty, or unparseable
    """

    # Convert strings into a Path object
    path = Path(file_path)

    # Make sure the selected path points to an existing file.
    if not path.is_file():
        raise CsvImportError(
            f"The selected file does not exist: {path}"
        )

    # Only accept files whose extension is .csv.
    # lower() also accepts uppercase extensions such as .CSV.
    if path.suffix.lower() != ".csv":
        raise CsvImportError(
            "DevSprig currently supports CSV files only."
        )

    try:
        # Load the file into a pandas DataFrame.
        # dtype=str tells pandas to preserve every imported value as text
        # The calculation files can convert the appropriate columns into numbers later.
        # keep_default_na=False keeps empty cells as empty strings instead of changing them into pandas NaN values.
        # utf-8-sig supports ordinary UTF-8 files as well as UTF-8 files containing a byte-order mark.
        responses = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
        )

    except EmptyDataError as error:
        raise CsvImportError(
            "The selected CSV file is empty."
        ) from error

    except ParserError as error:
        raise CsvImportError(
            "The selected file could not be parsed as a valid CSV."
        ) from error

    except UnicodeDecodeError as error:
        raise CsvImportError(
            "The selected CSV does not use a supported text encoding."
        ) from error

    except OSError as error:
        raise CsvImportError(
            f"DevSprig could not open the selected file: {error}"
        ) from error

    # A CSV may technically load but contain no columns.
    if len(responses.columns) == 0:
        raise CsvImportError(
            "The selected CSV does not contain any columns."
        )

    # Remove accidental spaces from the beginning or end of headings.
    responses.columns = [
        str(column).strip()
        for column in responses.columns
    ]

    # Identify every question by examining its heading and values.
    questions: list[QuestionInfo] = []

    for column_name in responses.columns:
        # Select the current column as a pandas Series.
        column_values = responses[column_name]

        # Detect the current column's question type.
        question = identify_question(
            column_name=column_name,
            values=column_values,
        )

        # Store the result.
        questions.append(question)

    return responses, questions

def identify_question(column_name: str, values: pd.Series) -> QuestionInfo:
    # Identifies the analysis type of a csv column
    # Look for a DevSprig template match, then make inference
    
    # Normalize the heading before looking it up
    normalized_name = normalize_header(column_name)
    
    # Exact template matches are the most reliable option
    if normaliez_name in OFFICIAL_TEMPLATE_QUESTIONS:
        (question_type, scale_minimum, scale_maximum, higher_is_better) = OFFICIAL_TEMPLATE_QUESTIONS[normalized_name]
        
        return QuestionInfo(
            column_name = column_name,
            question_type = question_type,
            confidence = DetectionConfidence.HIGH,
            detection_reason=("The column matches an official DevSprig template question."),
            scale_minimum = scale_minimum,
            scale_maximum = scale_maximum,
            higher_is_better = higher_is_better
        )
    # No official match was found
    return infer_custom_question(column_name = column_name, values = values)

def infer_custom_question(column_name: str, values: pd.Series) -> QuestionInfo:
    """
    Infers the type of a custom question
    Less reliable than exact matches
    """
    
    normalized_name = normalize_header(column_name)
    
    # Convert all values into stripped strings
    cleaned_values = values.astype(str).str.strip()
    
    # Remove blank responses before inspecting the values
    non_blank_values = cleaned_values[cleaned_values != ""]
    
    # A completely blank custom column can't be identified
    if non_blank_values.empty:
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.UNKNOWN,
            confidence = DetectionConfidence.LOW,
            detection_reason = ("The column contains no submitted values.")
        )
    
    # Detect timestamps by their heading
    if "timestamp" in normalized_name:
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.TIMESTAMP,
            confidence= DetectionConfidence.HIGH,
            detection_reason = ("The column heading contains the word 'timestamp'.")
        )
    
    # Detect participant or response identifiers
    identifier_phrases = (
        "participant id",
        "response id",
        "user id",
        "tester id"
    )
    
    if any(phrase in normalized_name for phrase in identifier_phrases):
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.IDENTIFIER,
            confidence = DetectionConfidence.HIGH,
            detection_reason = ("The column heading describes an identifier.")
        )
    
    # Detect task-completion questions before ordinary categories
    if ("complete" in normalized_name and "task" in normalized_name):
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.TASK_COMPLETION,
            confidence = DetectionConfidence.HIGH,
            detection_reason = ("The heading refers to completing a task.")
        )
    
    # Detect time or duration questions
    duration_phrases = (
        "how long",
        "duration",
        "minutes",
        "seconds",
        "hours",
        "time taken"
    )
    
    if any(phrase in normalized_name for phrase in duration_phrases):
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.NPS,
            confidence = DetectionConfidence.MEDIUM,
            detection_reason = ("The heading asks about recommendation likelihood."),
            scale_minimum = 0,
            scale_maximum = 10,
            higher_is_better = True
        )
    
    # Detect likely checkbox questions using both the heading and the presense of comma-separated selections
    checkbox_phrases = (
        "select all",
        "check all",
        "which problems",
        "which issues",
        "which features"
    )
    
    contains_checkbox_phrase = any(phrase in normalized_name for phrase in checkbox_phrases)
    
    contains_multiple_selections = any(", " in value for value in non_blank_values)
    
    if (contains_checkbox_phrase or contains_multiple_selections):
        return QuestionInfo(
            column_name = column_name,
            question_type = QuestionType.CHECKBOXES,
            confidence = DetectionConfidence.MEDIUM,
            detection_reason = ("The heading r submitted values suggest that multiple choices could be selected.")
        )
    
    # Try converting the submitted answers into numbers
    numeric_values = pd.to_numeric(non_blank_values, errors="coerce")
    
    # Calculate the proportion of nonblank values successfully converted
    numeric_ratio = numeric_values.notna().mean()
    
    # Keep only successfully converted values
    valid_numeric_values = numeric_values.dropna()
    
    # A mostly numeric column with a small integer range is probably a rating scale
    if 