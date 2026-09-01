const repos = [
  "microsoft/guidance",
  "microsoft/llguidance",
  "noamgat/lm-format-enforcer",
  "guardrails-ai/guardrails",
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

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

for (const r of repos) {
  let j = null;
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const res = await fetch(`https://api.github.com/repos/${r}`, {
        headers: { "User-Agent": "mo-yan-research", Accept: "application/vnd.github+json" },
        redirect: "follow",
      });
      if (res.status === 301 || res.status === 302) {
        console.log(`${r} -> REDIRECT ${res.headers.get("location")}`);
        j = { redirect: true };
        break;
      }
      if (res.ok) {
        j = await res.json();
        break;
      }
      if (res.status === 404) {
        console.log(`${r} -> NOT FOUND`);
        j = { notfound: true };
        break;
      }
    } catch (e) {
      // keep retrying
    }
    await sleep(4000);
  }
  if (j && !j.redirect && !j.notfound) {
    console.log(
      `${j.full_name} | ★${j.stargazers_count} | ${j.language || "-"} | ${(j.description || "").slice(0, 120)}`
    );
  } else if (!j) {
    console.log(`${r} -> FAILED after retries`);
  }
  await sleep(1500);
}