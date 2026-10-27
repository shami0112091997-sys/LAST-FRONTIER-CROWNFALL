"""M138 tests: synthetic ADB responses, no actual device or ADB calls."""
import unittest
from unittest.mock import patch

import M138_Android_Boot_Exit_Evidence_ReadOnly as m138
from M123_Private_Android_Exit_Triage_ReadOnly import triage


class EvidenceTests(unittest.TestCase):
    def test_similarly_named_packages_are_not_crownfall(self):
        for suffix in (".other", "2", "_backup", "-other"):
            with self.subTest(suffix=suffix):
                status, hits, selected = triage(
                    f"Process: {m138.PKG}{suffix}, PID: 100\nFATAL EXCEPTION\n")
                self.assertEqual(status, "NO_PACKAGE_EVIDENCE")
                self.assertEqual(selected, 0)
                self.assertTrue(all(count == 0 for count in hits.values()))

    def test_similarly_named_start_proc_does_not_capture_pid(self):
        status, hits, selected = triage(
            f"Start proc 100:{m138.PKG}.other/u0a123\n"
            "11-22 12:00:00.000 100 100 E AndroidRuntime: FATAL EXCEPTION\n")
        self.assertEqual(status, "NO_PACKAGE_EVIDENCE")
        self.assertEqual(selected, 0)
        self.assertEqual(hits["JAVA_EXCEPTION"], 0)

    def test_named_crownfall_subprocess_pid_is_recognized(self):
        status, hits, selected = triage(
            f"Process: {m138.PKG}:renderer, PID: 100\n"
            "11-22 12:00:00.000 100 100 E AndroidRuntime: FATAL EXCEPTION\n"
            "11-22 12:00:00.001 999 999 E AndroidRuntime: FATAL EXCEPTION\n")
        self.assertEqual(status, "PACKAGE_PID_FOUND")
        self.assertEqual(hits["JAVA_EXCEPTION"], 1)
        self.assertEqual(selected, 2)

    def test_single_device(self):
        self.assertEqual(m138.select_authorized_device("List of devices attached\nTESTER device\n"), "TESTER")
        self.assertIsNone(m138.select_authorized_device("List of devices attached\nTESTER device\nOTHER device\n"))
        self.assertIsNone(m138.select_authorized_device("List of devices attached\nTESTER unauthorized\n"))
        self.assertIsNone(m138.select_authorized_device("List of devices attached\nTESTER device\nOTHER offline\n"))

    def test_versions(self):
        self.assertEqual(m138.parse_version("versionCode=218 minSdk=26 versionCode=218"), 218)
        self.assertIsNone(m138.parse_version("versionCode=214 versionCode=218"))
        self.assertIsNone(m138.parse_version("no version"))

    def test_mocks_only_read_and_sanitize(self):
        commands = []
        def fake_read(argv, timeout=20):
            commands.append(argv)
            if argv == ["devices"]:
                return "List of devices attached\nsecret-serial device\n"
            if argv[-3:] == ["pm", "path", m138.PKG]:
                return "package:/data/app/private/secret.apk\n"
            if argv[-3:] == ["dumpsys", "package", m138.PKG]:
                return "versionCode=218 minSdk=26\n"
            if "logcat" in argv:
                return ("11-22 12:00:00.000 100 500 E AndroidRuntime: "
                        "Process: com.crownfall.stronghold, PID: 100\n"
                        "11-22 12:00:00.001 100 500 E AndroidRuntime: "
                        "FATAL EXCEPTION password=x\n")
            return "No exit info\n"
        with patch.object(m138.shutil, "which", return_value="/fake/adb"), patch.object(m138, "read_adb", side_effect=fake_read):
            result, rc = m138.collect()
        self.assertEqual(rc, 0)
        self.assertEqual(result["installed_version_code"], 218)
        self.assertTrue(all("install" not in c and "clear" not in c and "start" not in c for c in commands))
        self.assertNotIn("secret-serial", str(result))
        self.assertNotIn("password=x", str(result))
        self.assertNotIn("/data/app/private", str(result))
        self.assertEqual(result["root_cause"], "UNCONFIRMED")
        self.assertEqual(result["log_time_correlation"], "NOT_ESTABLISHED")

    def test_device_missing(self):
        with patch.object(m138.shutil, "which", return_value="/fake/adb"), patch.object(m138, "read_adb", return_value="List of devices attached\n"):
            result, rc = m138.collect()
        self.assertEqual(rc, 2)
        self.assertEqual(result["status"], "BLOCKED_EXACTLY_ONE_AUTHORIZED_DEVICE_REQUIRED")


if __name__ == "__main__":
    unittest.main()
