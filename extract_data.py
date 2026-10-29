from pathlib import Path
import shutil
import tarfile

project = Path(r"E:\clarity_cpc2")
archive_path = project / "data/archives/clarity_CPC2_data.v1_1.tgz"
destination = project / "data/extracted"
destination.mkdir(parents=True, exist_ok=True)
destination = destination.resolve()

extracted = 0
skipped_links = 0

print("Reading the archive. This may take several minutes.", flush=True)

with tarfile.open(archive_path, mode="r|gz") as archive:
    for member in archive:
        # Partition links are unsupported on exFAT.
        # We will use the actual audio in HA_outputs/signals instead.
        if member.issym() or member.islnk():
            skipped_links += 1
            continue

        if not member.isfile():
            continue

        output_path = (destination / member.name).resolve()

        # Prevent archive entries from writing outside our data folder.
        if not output_path.is_relative_to(destination):
            raise ValueError(f"Unsafe archive path: {member.name}")

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to a temporary file so an interrupted copy is identifiable.
        temporary_path = output_path.with_name(output_path.name + ".partial")

        source = archive.extractfile(member)
        if source is None:
            raise RuntimeError(f"Cannot read: {member.name}")

        with source, temporary_path.open("wb") as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)

        temporary_path.replace(output_path)
        extracted += 1

        if extracted % 500 == 0:
            print(f"Extracted {extracted:,} files...", flush=True)

print(f"Finished: {extracted:,} files extracted.")
print(f"Skipped {skipped_links:,} links.")

audio = (
    destination
    / "clarity_CPC2_data/clarity_data/HA_outputs/signals/CEC2"
    / "S09161_L0221_E022.wav"
)
print("Example audio exists:", audio.exists())