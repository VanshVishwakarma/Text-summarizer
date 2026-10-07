const dialogueBox = document.getElementById("dialogue");
const summarizeBtn = document.getElementById("summarizeBtn");
const summaryBox = document.getElementById("summary");


summarizeBtn.addEventListener("click", async function () {

    // Get dialogue entered by the user
    const dialogue = dialogueBox.value.trim();

    // Check if dialogue is empty
    if (!dialogue) {
        summaryBox.innerText = "Please enter a dialogue first.";
        return;
    }

    // Show loading state
    summarizeBtn.disabled = true;
    summarizeBtn.innerText = "Summarizing...";
    summaryBox.innerText = "Generating summary...";

    try {

        // Send dialogue to FastAPI
        const response = await fetch("/summarize/", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                dialogue: dialogue
            })
        });


        // Check if request was successful
        if (!response.ok) {
            throw new Error("Failed to generate summary.");
        }


        // Convert JSON response into JavaScript object
        const data = await response.json();


        // Display generated summary
        summaryBox.innerText = data.summary;

    }

    catch (error) {

        summaryBox.innerText =
            "Something went wrong while generating the summary.";

        console.error(error);

    }

    finally {

        // Restore button
        summarizeBtn.disabled = false;
        summarizeBtn.innerText = "Summarize";

    }

});