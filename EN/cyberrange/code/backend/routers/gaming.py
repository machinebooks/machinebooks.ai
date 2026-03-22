# Companion code for "The Cyber Range and the Machine" — Chapter 12
# Gaming zone endpoints: flag submission, leaderboard, challenge listing.
# This is STARTER code — not production-ready.

import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from auth import get_current_user, role_required

router = APIRouter()


# -- Rate limiting (Chapter 12: anti-brute-force for flag submission) ------
# In-memory rate limiter. Use Redis in production.

_submission_timestamps: dict[int, list[float]] = defaultdict(list)
MAX_SUBMISSIONS_PER_MINUTE = 10


def check_rate_limit(user_id: int) -> None:
    """Prevent brute-force flag guessing with per-user rate limiting."""
    now = time.time()
    cutoff = now - 60
    recent = [t for t in _submission_timestamps[user_id] if t > cutoff]
    _submission_timestamps[user_id] = recent

    if len(recent) >= MAX_SUBMISSIONS_PER_MINUTE:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many submissions. Wait 60 seconds.",
        )
    _submission_timestamps[user_id].append(now)


# -- Schemas ---------------------------------------------------------------

class FlagSubmission(BaseModel):
    challenge_id: int
    flag: str


class ChallengeOut(BaseModel):
    id: int
    title: str
    category: str
    difficulty: str
    points: int
    solved_by: int  # Number of solvers


class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    team: str | None
    score: int
    solves: int


class SubmissionResult(BaseModel):
    correct: bool
    points_awarded: int
    message: str


# -- Endpoints -------------------------------------------------------------

@router.get("/challenges", response_model=list[ChallengeOut])
async def list_challenges(
    category: str | None = None,
    user: dict = Depends(get_current_user),
):
    """
    List all active challenges, optionally filtered by category.

    Chapter 12: challenges are grouped by category (web, pwn, crypto, etc.)
    and show solve count for social proof / difficulty estimation.
    """
    # TODO: query Challenge model from database
    # Stub response for demonstration
    challenges = [
        ChallengeOut(
            id=1,
            title="SQL Injection 101",
            category="web",
            difficulty="easy",
            points=100,
            solved_by=42,
        ),
        ChallengeOut(
            id=2,
            title="Buffer Overflow Basics",
            category="pwn",
            difficulty="medium",
            points=200,
            solved_by=15,
        ),
    ]

    if category:
        challenges = [c for c in challenges if c.category == category]

    return challenges


@router.post("/submit-flag", response_model=SubmissionResult)
async def submit_flag(
    submission: FlagSubmission,
    user: dict = Depends(role_required("player")),
):
    """
    Submit a flag for a challenge.

    Chapter 12 covers the validation pipeline:
    1. Rate limit check (anti-brute-force)
    2. Format validation (quick reject malformed flags)
    3. Timing-safe comparison (hmac.compare_digest)
    4. Score calculation (dynamic scoring)
    5. Audit log entry
    """
    user_id = int(user["sub"])

    # Step 1: Rate limit
    check_rate_limit(user_id)

    # Step 2: Format check
    if not submission.flag.startswith("CYBERRANGE{"):
        return SubmissionResult(
            correct=False,
            points_awarded=0,
            message="Invalid flag format.",
        )

    # Step 3: Validate flag
    # TODO: look up challenge, get expected flag hash, use validate_flag_by_hash()
    # from services.flag_service import validate_flag_by_hash
    #
    # expected_hash = db.query(CtfFlag).filter_by(challenge_id=submission.challenge_id).first()
    # is_correct = validate_flag_by_hash(submission.flag, expected_hash.flag_hash)

    # Stub: always return incorrect for safety
    is_correct = False
    points = 0

    if is_correct:
        # Step 4: Calculate dynamic score
        # points = calculate_dynamic_score(base_points, total_solves)
        pass

    # Step 5: Log the attempt (always, for audit)
    # TODO: insert ScoreLog entry

    return SubmissionResult(
        correct=is_correct,
        points_awarded=points,
        message="Correct! Well done." if is_correct else "Incorrect flag. Try again.",
    )


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 50,
    user: dict = Depends(get_current_user),
):
    """
    Get the current CTF leaderboard.

    Chapter 12: leaderboard is sorted by score descending, with
    tiebreaker on earliest last solve timestamp.
    """
    # TODO: aggregate ScoreLog entries grouped by user
    # Stub response
    return [
        LeaderboardEntry(rank=1, username="alice", team="Red Phoenix", score=1500, solves=12),
        LeaderboardEntry(rank=2, username="bob", team="Blue Storm", score=1200, solves=10),
        LeaderboardEntry(rank=3, username="charlie", team=None, score=900, solves=8),
    ]
