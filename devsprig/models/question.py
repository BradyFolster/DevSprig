#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file does no importing or calculations.
It only defines the types of questions that DevSprig understands.
"""

from dataclasses import dataclass

from enum import Enum

class QuestionType(str, Enum):
    # These don't all match up exactly to google forms
    # Ex. Multiple Choice & Dropdown are both "CATEGORY" since
    # they are calculated the same way.
    
    TIMESTAMP = "timestamp"
    IDENTIFIER = "identifier"
    CATEGORY = "category"
    CHECKBOXES = "checkboxes"
    RATING_SCALE = "rating_scale"
    TASK_COMPLETION = "task_completion"
    DURATION = "duration"
    NPS = "nps"
    WRITTEN_RESPONSE = "written_response"
    UNKNOWN = "unknown"

class DetectionConfidence(str, Enum):
    # Describes how certain DevSprig is about a certain question type
    
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass(frozen=True)
class QuestionInfo:
    """
    Store information about one column imported from the csv
    
    frozen=True makes instances read-only after creation.
    """
    
    # The exact column heading in the csv
    column_name: str 
    
    # DevSprig's dedicated analysis type
    question_type: QuestionType
    
    # Confidence level
    confidence: DetectionConfidence 
    
    # A readable explanation of why the type was selected
    detection_reason: str 
    
    # These are used only for rating-scale questions
    # Other question types leave them as "None"
    scale_minimum: int | None = None
    scale_maximum: int | None = None
    
    # For rating scales, if higher is actually better on the scale
    higher_is_better: bool | None = None