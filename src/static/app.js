document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";
      
      // Clear and reset activity select dropdown
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-section">
            <h5>Current Participants:</h5>
            ${details.participants.length > 0 
              ? `<ul class="participants-list">
                   ${details.participants.map(participant => `
                     <li>
                       <span class="participant-email">${participant}</span>
                       <button class="delete-btn" onclick="removeParticipant('${name}', '${participant}')" title="Remove participant">
                         ✕
                       </button>
                     </li>
                   `).join('')}
                 </ul>`
              : '<p class="no-participants">No participants yet - be the first to sign up!</p>'
            }
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      console.error("Error fetching activities:", error);
      activitiesList.innerHTML = `<p>Failed to load activities. Please try again later.</p>`;
      // Don't clear the select dropdown on error, keep existing options
    }
  }

  // Function to remove a participant from an activity
  async function removeParticipant(activityName, participantEmail) {
    if (!confirm(`Are you sure you want to remove ${participantEmail} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/participants/${encodeURIComponent(participantEmail)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        
        // Show loading state and refresh after a small delay
        activitiesList.innerHTML = "<p>Updating activities...</p>";
        
        setTimeout(async () => {
          try {
            await fetchActivities();
          } catch (refreshError) {
            console.error("Error refreshing activities:", refreshError);
            activitiesList.innerHTML = "<p>Failed to refresh activities. Please reload the page.</p>";
          }
        }, 100);
      } else {
        messageDiv.textContent = result.detail || "An error occurred while removing participant";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to remove participant. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error removing participant:", error);
    }
  }

  // Make removeParticipant available globally for onclick handlers
  window.removeParticipant = removeParticipant;

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        
        // Show loading state and refresh after a small delay
        activitiesList.innerHTML = "<p>Updating activities...</p>";
        
        setTimeout(async () => {
          try {
            await fetchActivities();
          } catch (refreshError) {
            console.error("Error refreshing activities:", refreshError);
            activitiesList.innerHTML = "<p>Failed to refresh activities. Please reload the page.</p>";
          }
        }, 100);
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
