from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.evidence import UploaderRole, EvidenceType, CredibilityLabel


class EvidenceCreate(BaseModel):
    uploader: UploaderRole
    type: EvidenceType
    credibility: CredibilityLabel
    summary: str
    file_path: str | None = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    dispute_id: str
    uploader: UploaderRole
    type: EvidenceType
    credibility: CredibilityLabel
    summary: str
    file_path: str | None = None
    created_at: datetime
