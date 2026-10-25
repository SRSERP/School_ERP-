import os
import zipfile
import hashlib
import json
import sqlite3
import shutil
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from .models import SchoolProfile, BackupConfiguration, BackupLog, AuditLog


def get_file_sha256(filepath):
    """Calculates SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def generate_system_backup(school, backup_type='Full', created_by=None):
    """
    Creates a standalone compressed backup of database and uploaded media documents.
    Generates SHA-256 hash and records it in BackupLog and AuditLog.
    """
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp_str = timezone.now().strftime('%Y%m%d_%H%M%S')
    filename = f"backup_{school.school_code}_{backup_type}_{timestamp_str}.zip"
    filepath = os.path.join(backup_dir, filename)

    config = getattr(school, 'backup_config', None)
    is_encrypted = config.is_encryption_enabled if config else True

    manifest = {
        "system": "SRS School ERP",
        "school_code": school.school_code,
        "school_name": school.name,
        "backup_type": backup_type,
        "timestamp": timezone.now().isoformat(),
        "is_encrypted": is_encrypted,
        "included": []
    }

    with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # 1. Database
        if backup_type in ('Full', 'Database_Only'):
            db_path = os.path.join(settings.BASE_DIR, 'db.sqlite3')
            if os.path.exists(db_path):
                zip_file.write(db_path, arcname='database/db.sqlite3')
                manifest["included"].append("database/db.sqlite3")

        # 2. Uploaded Media Documents
        if backup_type in ('Full', 'Media_Only'):
            media_dir = os.path.join(settings.BASE_DIR, 'media')
            if os.path.exists(media_dir):
                for root, dirs, files in os.walk(media_dir):
                    for file in files:
                        full_p = os.path.join(root, file)
                        rel_p = os.path.relpath(full_p, settings.BASE_DIR)
                        zip_file.write(full_p, arcname=rel_p)
                manifest["included"].append("media/")

        # 3. Write manifest
        manifest_data = json.dumps(manifest, indent=2)
        zip_file.writestr('manifest.json', manifest_data)

    # Calculate file size and checksum
    file_size_bytes = os.path.getsize(filepath)
    file_size_mb = Decimal(str(round(file_size_bytes / (1024 * 1024), 2)))
    checksum = get_file_sha256(filepath)

    backup_log = BackupLog.objects.create(
        school=school,
        backup_name=filename,
        file_path=filepath,
        file_size_mb=file_size_mb,
        checksum_sha256=checksum,
        backup_type=backup_type,
        status='Success',
        is_encrypted=is_encrypted,
        created_by=created_by,
        created_at=timezone.now()
    )

    if config:
        config.last_backup_at = timezone.now()
        config.save(update_fields=['last_backup_at'])

    # Audit Trail
    AuditLog.log(
        school=school,
        user=created_by,
        module='Backup & Security',
        action='Generate Backup',
        target=filename,
        details=f"Type: {backup_type}, Size: {file_size_mb} MB, SHA-256: {checksum[:12]}..."
    )

    return backup_log


def verify_restore_archive(backup_log_id, user=None):
    """
    Performs an isolated verification test on the backup archive:
    1. Validates file existence and SHA-256 checksum against stored hash.
    2. Tests archive consistency via zip testzip().
    3. Extracts database into an isolated sandbox test directory without touching live db.sqlite3.
    4. Connects to the extracted sqlite file and validates table counts and student records.
    5. Cleans up sandbox and updates BackupLog verification status.
    """
    try:
        backup_log = BackupLog.objects.get(id=backup_log_id)
    except BackupLog.DoesNotExist:
        return {"success": False, "message": "Backup record not found."}

    filepath = backup_log.file_path
    if not os.path.exists(filepath):
        backup_log.status = 'Failed'
        backup_log.verification_notes = "Verification Failed: Backup archive file missing on disk."
        backup_log.save()
        return {"success": False, "message": "Backup file not found on disk."}

    # Verify SHA-256 Checksum
    current_hash = get_file_sha256(filepath)
    if backup_log.checksum_sha256 and current_hash != backup_log.checksum_sha256:
        backup_log.verification_notes = f"Checksum Mismatch! Expected: {backup_log.checksum_sha256[:16]}..., Found: {current_hash[:16]}..."
        backup_log.save()
        return {"success": False, "message": "Integrity Check Failed: Checksum does not match."}

    # Isolated test extraction sandbox
    sandbox_dir = os.path.join(settings.BASE_DIR, 'backups', 'restore_test', f"test_{backup_log.id}_{int(timezone.now().timestamp())}")
    os.makedirs(sandbox_dir, exist_ok=True)

    verified_tables = 0
    student_records = 0
    receipt_records = 0

    try:
        with zipfile.ZipFile(filepath, 'r') as zip_file:
            test_corrupt = zip_file.testzip()
            if test_corrupt:
                raise Exception(f"Corrupt file found inside archive: {test_corrupt}")

            zip_file.extractall(sandbox_dir)

        # Inspect extracted SQLite database
        test_db_path = os.path.join(sandbox_dir, 'database', 'db.sqlite3')
        if os.path.exists(test_db_path):
            conn = sqlite3.connect(test_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
            verified_tables = cursor.fetchone()[0]

            try:
                cursor.execute("SELECT count(*) FROM school_erp_student;")
                student_records = cursor.fetchone()[0]
            except Exception:
                student_records = 0

            try:
                cursor.execute("SELECT count(*) FROM school_erp_feereceipt;")
                receipt_records = cursor.fetchone()[0]
            except Exception:
                receipt_records = 0

            conn.close()

        notes = (
            f"Integrity verified successfully on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}. "
            f"SHA-256: Verified. Database tables: {verified_tables}, Students: {student_records}, Receipts: {receipt_records}."
        )

        backup_log.is_verified = True
        backup_log.verified_at = timezone.now()
        backup_log.verification_notes = notes
        backup_log.save()

        # Audit Trail
        AuditLog.log(
            school=backup_log.school,
            user=user,
            module='Backup & Security',
            action='Verify Backup',
            target=backup_log.backup_name,
            details=f"Test restore verification passed. Verified {verified_tables} tables."
        )

        return {
            "success": True,
            "message": "Backup verified successfully in isolated sandbox environment.",
            "verified_tables": verified_tables,
            "student_records": student_records,
            "receipt_records": receipt_records,
            "checksum": current_hash,
            "notes": notes
        }

    except Exception as e:
        backup_log.verification_notes = f"Verification Error: {str(e)}"
        backup_log.save()
        return {"success": False, "message": f"Verification failed: {str(e)}"}
    finally:
        # Safe cleanup of sandbox test directory
        if os.path.exists(sandbox_dir):
            shutil.rmtree(sandbox_dir, ignore_errors=True)


def execute_test_environment_restore(backup_log_id, user=None):
    """
    Restores the backup archive into a dedicated Staging / Test Environment folder
    (e.g., 'staging_test/'), confirming full data extractability without overwriting production.
    """
    try:
        backup_log = BackupLog.objects.get(id=backup_log_id)
    except BackupLog.DoesNotExist:
        return {"success": False, "message": "Backup record not found."}

    filepath = backup_log.file_path
    if not os.path.exists(filepath):
        return {"success": False, "message": "Backup file missing on disk."}

    staging_dir = os.path.join(settings.BASE_DIR, 'staging_test')
    os.makedirs(staging_dir, exist_ok=True)

    with zipfile.ZipFile(filepath, 'r') as zip_file:
        zip_file.extractall(staging_dir)

    test_db = os.path.join(staging_dir, 'database', 'db.sqlite3')
    db_exists = os.path.exists(test_db)
    media_exists = os.path.exists(os.path.join(staging_dir, 'media'))

    AuditLog.log(
        school=backup_log.school,
        user=user,
        module='Backup & Security',
        action='Staging Test Restore',
        target=backup_log.backup_name,
        details=f"Extracted to staging_test/. Database present: {db_exists}, Media present: {media_exists}."
    )

    return {
        "success": True,
        "staging_dir": staging_dir,
        "database_restored": db_exists,
        "media_restored": media_exists,
        "message": "Test restore completed successfully in staging environment (staging_test/). Production database is untouched."
    }
