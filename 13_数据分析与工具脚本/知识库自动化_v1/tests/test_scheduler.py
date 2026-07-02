import plistlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from kb_automation.scheduler import install_launchd, render_launchd_plist


class SchedulerTests(unittest.TestCase):
    def test_plist_runs_daily_pipeline_with_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp).resolve()
            module = vault / "13_数据分析与工具脚本/知识库自动化_v1"
            module.mkdir(parents=True)
            run_py = module / "run.py"
            run_py.write_text("", encoding="utf-8")

            payload = plistlib.loads(
                render_launchd_plist(vault, python_executable="/usr/bin/python3", hour=9, minute=15)
            )

            self.assertEqual(payload["Label"], "com.shengguo.retail-knowledge-vault.automation")
            self.assertEqual(
                payload["ProgramArguments"],
                ["/usr/bin/python3", str(run_py), "run", "--vault", str(vault)],
            )
            self.assertEqual(payload["StartCalendarInterval"], {"Hour": 9, "Minute": 15})
            self.assertNotIn("launchctl", render_launchd_plist(vault).decode("utf-8"))

    def test_install_validates_then_bootstraps_and_kickstarts(self):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            agents = Path(tmp) / "LaunchAgents"
            module = vault / "13_数据分析与工具脚本/知识库自动化_v1"
            module.mkdir(parents=True)
            (module / "run.py").write_text("", encoding="utf-8")
            calls = []

            def runner(args, **kwargs):
                calls.append(args)
                return subprocess.CompletedProcess(args, 0, "", "")

            installed = install_launchd(
                vault,
                launch_agents_dir=agents,
                uid=501,
                runner=runner,
            )

            self.assertTrue(installed.exists())
            self.assertEqual(calls[0][:2], ["plutil", "-lint"])
            self.assertEqual(calls[-2][0:2], ["launchctl", "bootstrap"])
            self.assertEqual(calls[-1][0:2], ["launchctl", "kickstart"])


if __name__ == "__main__":
    unittest.main()
