"""Schemas para políticos, partidos, mandatos."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


# --- Parties ---

class PartyResponse(BaseModel):
    id: uuid.UUID
    name: str
    acronym: str
    electoral_number: int | None = None
    logo_url: str | None = None
    status: str


# --- Politician Public ---

class PoliticianListItem(BaseModel):
    id: uuid.UUID
    full_name: str
    ballot_name: str | None = None
    slug: str
    photo_url: str | None = None
    current_status: str
    current_party: PartyResponse | None = None
    current_position_name: str | None = None
    state_code: str | None = None
    city_name: str | None = None


class PoliticianListResponse(BaseModel):
    items: list[PoliticianListItem]
    total: int
    page: int
    limit: int
    pages: int


class AliasResponse(BaseModel):
    id: uuid.UUID
    alias: str
    alias_type: str
    is_verified: bool


class SocialLinkResponse(BaseModel):
    id: uuid.UUID
    platform: str
    url: str
    username: str | None = None
    is_official: bool


class MembershipResponse(BaseModel):
    id: uuid.UUID
    party: PartyResponse
    started_at: date | None = None
    ended_at: date | None = None
    state_code: str | None = None
    is_current: bool


class MandateResponse(BaseModel):
    id: uuid.UUID
    position_name: str
    party_acronym: str | None = None
    state_code: str | None = None
    city_name: str | None = None
    started_at: date | None = None
    ended_at: date | None = None
    status: str


class PoliticianDetailResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    ballot_name: str | None = None
    slug: str
    biography: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    gender: str | None = None
    education: str | None = None
    occupation: str | None = None
    photo_url: str | None = None
    current_status: str
    current_party: PartyResponse | None = None
    current_position_name: str | None = None
    state_code: str | None = None
    city_name: str | None = None
    website_url: str | None = None
    is_verified: bool
    data_quality_score: float | None = None
    aliases: list[AliasResponse] = []
    social_links: list[SocialLinkResponse] = []
    updated_at: datetime
    source_url: str | None = None


class PoliticianSourceResponse(BaseModel):
    source_id: str | None
    source_url: str | None
    collected_at: datetime | None
    validated_at: datetime | None
    validated_by: str | None


# --- Admin Schemas ---

class PoliticianCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=500)
    ballot_name: str | None = Field(None, max_length=255)
    biography: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    gender: str | None = None
    marital_status: str | None = None
    education: str | None = None
    occupation: str | None = None
    photo_url: str | None = None
    state_code: str | None = Field(None, max_length=2)
    city_name: str | None = None
    website_url: str | None = None
    current_party_id: uuid.UUID | None = None
    current_position_id: uuid.UUID | None = None
    source_url: str | None = None


class PoliticianUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=500)
    ballot_name: str | None = None
    biography: str | None = None
    birth_date: date | None = None
    birth_place: str | None = None
    gender: str | None = None
    marital_status: str | None = None
    education: str | None = None
    occupation: str | None = None
    photo_url: str | None = None
    state_code: str | None = Field(None, max_length=2)
    city_name: str | None = None
    website_url: str | None = None
    current_status: str | None = None
    current_party_id: uuid.UUID | None = None
    current_position_id: uuid.UUID | None = None
    source_url: str | None = None


class AliasCreateRequest(BaseModel):
    alias: str = Field(min_length=1, max_length=500)
    alias_type: str = "ballot_name"
    source_id: str | None = None


class MembershipCreateRequest(BaseModel):
    party_id: uuid.UUID
    started_at: date | None = None
    ended_at: date | None = None
    state_code: str | None = None
    is_current: bool = False
    source_url: str | None = None


class MandateCreateRequest(BaseModel):
    position_id: uuid.UUID
    party_id: uuid.UUID | None = None
    state_code: str | None = None
    city_name: str | None = None
    started_at: date | None = None
    ended_at: date | None = None
    status: str = "in_office"
    source_url: str | None = None


class SocialLinkCreateRequest(BaseModel):
    platform: str
    url: str = Field(max_length=2048)
    username: str | None = None
    is_official: bool = False


class ChangeHistoryResponse(BaseModel):
    id: uuid.UUID
    field_name: str
    old_value: str | None
    new_value: str | None
    change_reason: str | None
    changed_by: str | None
    created_at: datetime
