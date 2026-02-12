// BEGIN isConditionMet
const isConditionMet = () => {
    console.log("🔍 Checking for 'Session 2' li element...");

    // 1️⃣ Find the Session 2 checkbox li
    const li = Array.from(document.querySelectorAll("li")).find(el =>
        Array.from(el.querySelectorAll("span")).some(s => s.textContent.trim() === "Session 2")
    );

    if (!li) {
        console.warn("❌ 'Session 2' li not found");
        return false;
    }
    console.log("✅ Found 'Session 2' li:", li);

    const checkbox = li.querySelector("input[type='checkbox']");
    if (!checkbox) {
        console.warn("❌ Checkbox not found inside 'Session 2' li");
        return false;
    }

    console.log("Checkbox found, checked:", checkbox.checked);

    // 2️⃣ Check if there are existing Session 2 blocks in timetable
    const timetableContainer = document.querySelector("#timetable_canvas");
    if (!timetableContainer) {
        console.warn("❌ Timetable container not found");
        return false;
    }

    const existingSession2Blocks = Array.from(
        timetableContainer.querySelectorAll(".timetableBlock.timetableSession .timetableBlockTitle")
    ).filter(title => title.textContent.includes("Session 2"));

    console.log("ℹ️ Existing Session 2 blocks count:", existingSession2Blocks.length);

    // ✅ Only trigger if checkbox is unchecked AND no Session 2 blocks exist
    const conditionMet = !checkbox.checked && existingSession2Blocks.length === 0;

    console.log("🔑 Condition met?", conditionMet);
    return conditionMet;
};
// END isConditionMet

// BEGIN onConditionMet
const onConditionMet = () => {
    console.log("🔍 Selecting timetable container...");

    const container = document.querySelector(
        "#timetable_canvas > div:nth-child(2) > div:nth-child(1)"
    );

    if (!container) {
        console.warn("❌ Timetable container not found");
        console.log("Current #timetable_canvas children:", document.querySelector("#timetable_canvas")?.children);
        return;
    }

    console.log("✅ Timetable container found:", container);

    const session2_2 = document.createElement("div");
    session2_2.className = "timetableBlock timetableSession";
    session2_2.style.position = "absolute";
    session2_2.style.top = "320px";
    session2_2.style.left = "55px";
    session2_2.style.height = "118px";
    session2_2.style.width = "647px";
    session2_2.style.backgroundColor = "rgb(236, 196, 149)";
    session2_2.style.color = "rgb(31, 17, 0)";
    session2_2.style.zIndex = "10";

    session2_2.innerHTML = `
        <span></span>
        <div class="entry-content" style="width:100%;height:100%;">
            <div class="timetableBlockWrapper">
                <div class="timetableBlockTitle">Session 2: Paper 2.2</div>
                <div class="timetableBlockConvener"></div>
            </div>
            <div class="timetableBlockWrapper" style="margin-top:auto;">
                <div class="timetableBlockLocation">
                    Conference Room, Conference Venue
                </div>
                <div class="timetableBlockTime">10:20 - 11:20</div>
            </div>
        </div>
    `;

    console.log("Appending new session block to container...");
    container.appendChild(session2_2);
    console.log("✅ New Session 2 block appended:", session2_2);
};
// END onConditionMet
