// 直接核实重点仓库元数据
const repos = [
  "microsoft/guidance",
  "microsoft/llguidance",
  "noamgat/lm-format-enforcer",
  "guardrails-ai/guardrails",
  "langchain-ai/langgraph",
  "RasaHQ/rasa",
  "pydantic/pydantic",
  "ShishirPatil/gorilla",
  "1rgs/jsonformer",
  "teddysum/EduChat",
  "Booth/Booth",
  "deshwalmahesh/PHUDGE",
  "iwangjian/Coding-Tutor",
  "umass-ml4ed/dialogue-kt",
  "tanchongmin/strictjson",
  "prefecthq/marvin",
];

for (const r of repos) {
  try {
    const res = await fetch(`https://api.github.com/repos/${r}`, {
      headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" },
      redirect: "follow",
    });
    if (res.status === 301 || res.status === 302) {
      const loc = res.headers.get("location");
      console.log(`${r} -> REDIRECT ${loc}`);
      continue;
    }
    if (!res.ok) {
      console.log(`${r} -> HTTP ${res.status}`);
      continue;
    }
    const j = await res.json();
    console.log(
      `${j.full_name} | ★${j.stargazers_count} | ${j.language || "-"} | ${(j.description || "").slice(0, 120)}`
    );
  } catch (e) {
    console.log(`${r} -> ERR ${e.message}`);
  }
  await new Promise((r2) => setTimeout(r2, 800));
}