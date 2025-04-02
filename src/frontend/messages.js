// your code goes here

// Establish a WebSocket connection with the server
const socket = io(window.location.host);

// script.js

document.addEventListener("DOMContentLoaded", () => {
    const messagesDiv = document.getElementById("messages");
    const userInput = document.getElementById("userInput");
    const sendButton = document.getElementById("sendButton");
    const checkboxes = document.querySelectorAll('input[name="topic"]');
    const allCheckbox = document.querySelector('input[name="topic"][value="all"]');

    // Function to add messages to the chat
    function addMessage(content, sender) {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message", sender);
        const profileImg = document.createElement("img");
        profileImg.classList.add("profile-pic");

        if (sender == "user") {
            setProfilePicture(profileImg, "max"); // Path to user's profile picture
            profileImg.alt = "User Profile";
        } else {
            setProfilePicture(profileImg, "prof_headshot_funny"); // Path to bot's profile picture
            profileImg.alt = "Bot Profile";
        }

        const messageContent = document.createElement("div");
        messageContent.classList.add("message-content");
        // const parsedContent = content.replace(/(https?:\/\/[^\s]+)/g,'<a href="$1" target="_blank">$1</a>'
        // );
        messageContent.innerHTML = content;
        messageDiv.appendChild(profileImg);
        messageDiv.appendChild(messageContent);
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function setProfilePicture(profileImg, username) {
        const pfpDir = "/profile_pic/";
        let pfpPath = `${pfpDir}`;

        if(username == "prof_headshot_funny"){
        pfpPath = `${pfpDir}${username}.jpg`;
        }

        else{
        pfpPath = `${pfpDir}${username}.png`;
        }
        profileImg.src = pfpPath;
    }    

    //event listener for the "All" checkbox
    allCheckbox.addEventListener("change", () => {
        const otherCheckboxes = document.querySelectorAll('input[name="topic"]:not([value="all"])');
    
        if (allCheckbox.checked) {
            // If "All" is checked, disable other checkboxes
            otherCheckboxes.forEach(checkbox => {
                checkbox.disabled = true;
                checkbox.checked = false;
            }); 
        } else {
            // If "All" is unchecked, enable other checkboxes
            otherCheckboxes.forEach(checkbox => checkbox.disabled = false);
        }
    });

    
    //function to get whatever topics the client selected
    function getSelectedTopics() {
        const checkboxes = document.querySelectorAll('input[name="topic"]:checked');
        const selected_topics = Array.from(checkboxes).map(checkbox => checkbox.value);
        console.log("selected topics: ", selected_topics);
        //if the ALL option is selected then special case
        if (selected_topics.includes("all")){
            return ["Health", "Environment", "Technology", "Economy", "Entertainment", "Sports", "Politics", "Education", "Travel", "Food"];
        }
        else if (selected_topics.length == 0){
            return [];
        }

        return selected_topics;
    }
    
    sendButton.addEventListener("click", () => {
        const message = userInput.value.trim();
        if (message) {
            addMessage(message, "user");
            let chitchat = true;
            const topics = getSelectedTopics();
            const topic_type = topics.length > 0 ? topics.join(", ") : "All";
            //if some topic(s) selected then not chitchat
            if(topics.length > 0){
                chitchat = false;
            }
            userInput.value = "";
            // Simulate bot response
            socket.send(JSON.stringify({"topic_type": topic_type, "query": message, "chitchat": chitchat}));
            // setTimeout(() => addMessage("Bot response to: " + message, "bot"), 500);
        }
        
    });

    function requestPlotData(plotType) {
        socket.send(JSON.stringify({ request_plot: true, plot_type: plotType }));
    }

    // Handle server response for plot data
    socket.on("plot_data", (response) => {
        const plotData = JSON.parse(response.data);
        if (response.type === "pie_chart") {
            console.log("goes to pie");
            Plotly.newPlot("pieChart", plotData);
        } else if (response.type === "timeseries") {
            Plotly.newPlot("timeSeries", plotData);
        }
        else{
            Plotly.newPlot("precision_terms_graph", plotData, plotData);
        }
    });

    // Called whenever data is received from the server over the WebSocket connection
    // Listen for the server's response to the message
    socket.on("message", (response) => {
        // Add bot's message to the chat with a delay
        setTimeout(() => addMessage(response, "bot"), 500);
        })
    
    
    // Allow pressing "Enter" to send message
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            sendButton.click();
        }
    });
});