import re

from app.domain.intake import IntakeIssue, IssueSeverity, NormalizedIntake, ValidationResult

ADDRESS_NUMBER_PATTERN = re.compile(r"\d+")


class IntakeValidationService:
    def validate(self, intake: NormalizedIntake) -> ValidationResult:
        issues: list[IntakeIssue] = []

        if not intake.title:
            issues.append(
                IntakeIssue(
                    code="MISSING_TITLE",
                    severity=IssueSeverity.ERROR,
                    message="Intake title is required before dispatch preparation.",
                    field_name="title",
                ),
            )

        if not intake.customer_name:
            issues.append(
                IntakeIssue(
                    code="MISSING_CUSTOMER_NAME",
                    severity=IssueSeverity.ERROR,
                    message="Customer name is required before dispatch preparation.",
                    field_name="customer_name",
                ),
            )

        if intake.scheduled_date is None:
            issues.append(
                IntakeIssue(
                    code="MISSING_SCHEDULED_DATE",
                    severity=IssueSeverity.ERROR,
                    message="Scheduled date is required before dispatch preparation.",
                    field_name="scheduled_date",
                ),
            )

        if not intake.location:
            issues.append(
                IntakeIssue(
                    code="MISSING_LOCATION",
                    severity=IssueSeverity.ERROR,
                    message="Service location is required before dispatch preparation.",
                    field_name="location",
                ),
            )
        elif not ADDRESS_NUMBER_PATTERN.search(intake.location):
            issues.append(
                IntakeIssue(
                    code="MALFORMED_LOCATION",
                    severity=IssueSeverity.ERROR,
                    message="Service location appears malformed or lacks a street number.",
                    field_name="location",
                ),
            )

        if len(intake.states) > 1:
            issues.append(
                IntakeIssue(
                    code="CONFLICTING_STATE_MARKERS",
                    severity=IssueSeverity.CRITICAL,
                    message="Multiple state markers were detected in the intake text.",
                    field_name="states",
                    metadata={"states": intake.states},
                ),
            )
        elif not intake.states:
            issues.append(
                IntakeIssue(
                    code="MISSING_STATE_MARKER",
                    severity=IssueSeverity.WARNING,
                    message="No supported state marker was detected.",
                    field_name="states",
                ),
            )

        if len(intake.time_windows) > 1:
            issues.append(
                IntakeIssue(
                    code="CONFLICTING_TIME_WINDOWS",
                    severity=IssueSeverity.CRITICAL,
                    message="Both AM and PM markers were detected in the intake text.",
                    field_name="time_windows",
                    metadata={"time_windows": tuple(intake.time_windows)},
                ),
            )

        if intake.cancellation.detected:
            issues.append(
                IntakeIssue(
                    code="CANCELLATION_DETECTED",
                    severity=IssueSeverity.CRITICAL,
                    message="Cancellation language was detected; dispatch must stop.",
                    field_name="title",
                    metadata={
                        "keyword_matches": intake.cancellation.keyword_matches,
                        "confidence": intake.cancellation.confidence,
                    },
                ),
            )

        if intake.water_emergency.detected:
            issues.append(
                IntakeIssue(
                    code="WATER_EMERGENCY_REQUIRES_WORKFLOW",
                    severity=IssueSeverity.WARNING,
                    message=(
                        "Water Emergency language was detected and requires "
                        "separate workflow review."
                    ),
                    field_name="title",
                    metadata={
                        "keyword_matches": intake.water_emergency.keyword_matches,
                        "confidence": intake.water_emergency.confidence,
                    },
                ),
            )

        return ValidationResult(
            issues=tuple(issues),
            is_dispatch_safe=is_dispatch_safe(issues),
        )


def is_dispatch_safe(issues: list[IntakeIssue]) -> bool:
    unsafe_codes = {
        "CANCELLATION_DETECTED",
        "WATER_EMERGENCY_REQUIRES_WORKFLOW",
    }
    return not any(
        issue.severity in {IssueSeverity.ERROR, IssueSeverity.CRITICAL}
        or issue.code in unsafe_codes
        for issue in issues
    )


validation_service = IntakeValidationService()
