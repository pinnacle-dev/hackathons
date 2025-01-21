from datetime import datetime
from dataclasses import dataclass
from typing import Literal, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from rcs import Pinnacle
from fpdf import FPDF
from typing import TypedDict
import requests
import uuid
from PIL import Image
from io import BytesIO

load_dotenv()

client = Pinnacle(
    api_key=os.environ["PINNACLE_API_KEY"],
)


class Note(TypedDict):
    contentType: Literal["text", "image"]
    content: str


@dataclass
class Notes:
    createdAt: datetime
    phoneNumber: str
    notes: list[Note]


# Initialize Supabase client
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


def get_notes(full_date: datetime, phone_number: str) -> Optional[Notes]:
    date = full_date.strftime("%Y-%m-%d")

    response = (
        supabase.table("Notes")
        .select("*")
        .eq("phoneNumber", phone_number)
        .eq("createdAt", date)
        .execute()
    )
    if response.data:
        return Notes(
            createdAt=response.data[0]["createdAt"],
            phoneNumber=response.data[0]["phoneNumber"],
            notes=response.data[0]["notes"],
        )
    else:
        return None


def add_or_create_note(full_date: datetime, phone_number: str, note: Note) -> bool:
    date = full_date.strftime("%Y-%m-%d")
    response = (
        supabase.table("Notes")
        .select("*")
        .eq("phoneNumber", phone_number)
        .eq("createdAt", date)
        .execute()
    )

    if response.data:
        notes = response.data[0]["notes"]
        notes.append(note)
        response = (
            supabase.table("Notes")
            .update({"notes": notes})
            .eq("phoneNumber", phone_number)
            .eq("createdAt", date)
            .execute()
        )
        return len(response.data) > 0

    else:
        response = (
            supabase.table("Notes")
            .insert(
                {
                    "createdAt": date,
                    "phoneNumber": phone_number,
                    "notes": [note],
                }
            )
            .execute()
        )
        return len(response.data) > 0


def convert_notes_to_pdf(notes: Notes) -> Optional[str]:

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, "Notes", 0, 1, "C")

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for note in notes.notes:
        if note["contentType"] == "text":
            pdf.multi_cell(0, 10, note["content"])
        elif note["contentType"] == "image":
            # Assuming content is a URL to the media
            image_url = get_download_url(note["content"])
            if image_url == None:
                return None

            response = requests.get(image_url)
            if response.status_code == 200:
                unique_image_path = f"/tmp/{uuid.uuid4()}.jpg"
                with open(unique_image_path, "wb") as img_file:
                    img_file.write(response.content)
                pdf.image(unique_image_path, w=100)
            else:
                print(f"Failed to download image from {image_url}")

    pdf_file_path = f"/tmp/{notes.phoneNumber}_{notes.createdAt}.pdf"
    pdf.output(pdf_file_path)

    folder_path = f"notes/{notes.phoneNumber}/{notes.createdAt}/notes.pdf"

    with open(pdf_file_path, "rb") as file:
        response = supabase.storage.from_("hackathons").upload(
            folder_path, file, {"upsert": "true", "content-type": "application/pdf"}
        )

    return get_download_url(response.path)


def upload_image(date_str: str, phone_number: str, image_url: str) -> Optional[str]:
    folder_path = f"notes/{phone_number}/{date_str}/media"
    file_name = f"{uuid.uuid4()}"

    response = requests.get(image_url)
    if response.status_code == 200:

        image = Image.open(BytesIO(response.content))
        if image.format != "JPEG":
            image = image.convert("RGB")
        image.save(f"/tmp/{file_name}.jpg", "JPEG")
        print("FINISHED SAVING IMAGE")
        with open(f"/tmp/{file_name}.jpg", "rb") as file:
            response = supabase.storage.from_("hackathons").upload(
                f"{folder_path}/{file_name}.jpg",
                file,
                {"upsert": "true", "content-type": "image/jpeg"},
            )

        return response.path

    return None


def get_download_url(path: str) -> Optional[str]:
    response = supabase.storage.from_("hackathons").create_signed_url(
        path,
        60 * 60 * 24,  # URL valid for 24 hours
    )
    return response["signedURL"]
