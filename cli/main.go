package main

import (
	"flag"
	"fmt"
	"os/exec"
	"strings"
)

func adb(args ...string) string {
	cmd := exec.Command("adb", append([]string{"shell"}, args...)...)
	out, _ := cmd.Output()
	return strings.TrimSpace(string(out))
}

func main() {
	audit := flag.Bool("audit", false, "Audit all apps")
	flag.Parse()

	if *audit {
		out := adb("pm", "list", "packages", "-3")
		for _, pkg := range strings.Split(out, "\n") {
			pkg = strings.TrimPrefix(pkg, "package:")
			if pkg == "" {
				continue
			}
			perms := adb("dumpsys", "package", pkg)
			if strings.Contains(perms, "ACCESS_FINE_LOCATION") {
				fmt.Printf("  ⚠️  %s\n", pkg)
			}
		}
	}
}
