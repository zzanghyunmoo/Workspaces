import configparser
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class WorkspaceContractTests(unittest.TestCase):
    def test_root_docs_directory_is_absent(self) -> None:
        self.assertFalse((ROOT / "docs").exists())

    def test_root_templates_do_not_require_docs_artifacts(self) -> None:
        for relative_path in (
            ".github/ISSUE_TEMPLATE/work.yml",
            ".github/pull_request_template.md",
        ):
            content = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertNotIn("docs/", content, relative_path)

    def test_notes_submodule_tracks_public_repository_main(self) -> None:
        config = configparser.ConfigParser()
        config.read(ROOT / ".gitmodules", encoding="utf-8")

        section = 'submodule "notes"'
        self.assertTrue(config.has_section(section))
        self.assertEqual(config.get(section, "path"), "notes")
        self.assertEqual(
            config.get(section, "url"),
            "https://github.com/zzanghyunmoo/notes-private.git",
        )
        self.assertEqual(config.get(section, "branch"), "main")


if __name__ == "__main__":
    unittest.main()
