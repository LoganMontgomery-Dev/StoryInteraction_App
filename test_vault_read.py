"""
Milestone 2: Test Vault Reading
Goal: Verify Python can read lore files from your Obsidian vault

Prerequisites:
1. Vault exists at C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault
2. At least one lore file exists

Run: python test_vault_read.py
"""

from pathlib import Path

def test_vault_read():
    print("=" * 50)
    print("MILESTONE 2: Testing Vault Reading")
    print("=" * 50)

    # Vault path from your .env
    vault_path = Path("C:/Users/Logan/Desktop/DOAMMO/__Doammo_Vault")

    print(f"\n[1/4] Checking if vault exists...")
    if not vault_path.exists():
        print(f"✗ ERROR: Vault not found at {vault_path}")
        print("Please check the path in your .env file")
        return False

    print(f"✓ Vault found at: {vault_path}")

    print(f"\n[2/4] Looking for lore files (Char_Aeth_*.md)...")

    # Find all character lore files
    lore_files = list(vault_path.glob("Char_Aeth_*.md"))

    if not lore_files:
        print("✗ No Char_Aeth_*.md files found")
        return False

    print(f"✓ Found {len(lore_files)} lore files:")
    for file in lore_files:
        size = file.stat().st_size
        print(f"  - {file.name} ({size} bytes)")

    print(f"\n[3/4] Reading Lyssia's character file...")

    lyssia_file = vault_path / "Char_Aeth_Lyssia.md"

    if not lyssia_file.exists():
        print("✗ Lyssia file not found")
        return False

    try:
        with open(lyssia_file, 'r', encoding='utf-8') as f:
            content = f.read()

        print(f"✓ Successfully read {len(content)} characters")

        print(f"\n[4/4] Preview of content (first 500 characters):")
        print("=" * 50)
        print(content[:500])
        if len(content) > 500:
            print("\n... (content continues)")
        print("=" * 50)

        print("\n✓ MILESTONE 2 COMPLETE!")
        print("Python can successfully read your Obsidian vault lore files.")
        print(f"Total lore files found: {len(lore_files)}")
        print()
        return True

    except Exception as e:
        print(f"✗ ERROR reading file: {e}")
        return False

if __name__ == "__main__":
    test_vault_read()
