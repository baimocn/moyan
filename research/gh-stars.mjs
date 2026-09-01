// 用 shields.io badge JSON 拿 star 数
const repos = [
  "guidance-ai/guidance",
  "microsoft/llguidance",
  "noamgat/lm-format-enforcer",
  "guardrails-ai/guardrails",
  "pydantic/pydantic",
  "RasaHQ/rasa",
  "1rgs/jsonformer",
  "prefecthq/marvin",
  "ShishirPatil/gorilla",
  "teddysum/EduChat",
  "567-labs/instructor",
  "dottxt-ai/outlines",
  "langchain-ai/langgraph",
  "quentin-mckay/AI-Quiz-Generator",
  "iwangjian/Coding-Tutor",
  "umass-ml4ed/dialogue-kt",
  "deshwalmahesh/PHUDGE",
  "tanchongmin/strictjson",
];
for (const r of repos) {
  try {
    const res = await fetch(`https://img.shields.io/github/stars/${r}.json`, {
      headers: { "User-Agent": "Mozilla/5.0" },
    });
    if (!res.ok) { console.log(`${r} -> HTTP ${res.status}`); continue; }
    const j = await res.json();
    console.log(`${r} -> ★${j.value}`);
  } catch (e) {
    console.log(`${r} -> ERR ${e.message}`);
  }
  await new Promise((r2) => setTimeout(r2, 1200));
}