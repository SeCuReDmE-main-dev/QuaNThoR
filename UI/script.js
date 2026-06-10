document.addEventListener('DOMContentLoaded', () => {
    const verifyButton = document.getElementById('verify-button');
    const proofEditor = document.getElementById('proof-editor');
    const resultsPanel = document.getElementById('results-panel');

    verifyButton.addEventListener('click', async () => {
        const mizarCode = proofEditor.value;
        if (!mizarCode.trim()) {
            alert('Please enter a Mizar proof to verify.');
            return;
        }

        // --- UI State: Loading ---
        verifyButton.disabled = true;
        verifyButton.classList.add('loading');
        verifyButton.textContent = 'Verifying...';
        resultsPanel.innerHTML = '<div class="placeholder"><p>AI Assistant is analyzing the proof...</p></div>';

        try {
            // --- API Call ---
            const response = await fetch('/verify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ code: mizarCode }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Error during verification:', error);
            resultsPanel.innerHTML = `<div class="verdict error"><strong>Error:</strong> Could not connect to the verification API. Please ensure the backend server is running.</div>`;
        } finally {
            // --- UI State: Reset ---
            verifyButton.disabled = false;
            verifyButton.classList.remove('loading');
            verifyButton.textContent = 'Verify Proof';
        }
    });

    // --- Function to Display Results in the UI ---
    function displayResults(data) {
        resultsPanel.innerHTML = ''; // Clear previous results

        const assistantResponse = data.ai_assistant;
        const status = data.status;

        // 1. Display the Verdict
        const verdictDiv = document.createElement('div');
        verdictDiv.classList.add('verdict');
        if (status === 'success') {
            verdictDiv.classList.add('success');
            verdictDiv.innerHTML = `<strong>Verdict:</strong> Verification successful`;
        } else {
            // Future logic for other statuses like logical proof errors
            verdictDiv.classList.add('error');
            verdictDiv.innerHTML = `<strong>Verdict:</strong> Analysis Complete`;
        }
        resultsPanel.appendChild(verdictDiv);


        // 2. Display Enhanced Human Explanation (with grammar improvements)
        const originalExplanation = assistantResponse.human_explanation;
        const enhancedExplanation = assistantResponse.grammar_enhanced_explanation || originalExplanation;
        
        const explanationCard = createResultCard('explanation', 'AI Mathematical Analysis', enhancedExplanation);
        resultsPanel.appendChild(explanationCard);
        
        // 2b. Display Grammar Improvements if any
        if (assistantResponse.grammar_suggestions && assistantResponse.grammar_suggestions.length > 0) {
            const grammarCard = createGrammarCard(assistantResponse.grammar_suggestions, assistantResponse.grammar_score);
            resultsPanel.appendChild(grammarCard);
        }

        // 3. Display Suggestion
        const suggestionCard = createResultCard('suggestion', 'Suggestion', assistantResponse.suggestion);
        resultsPanel.appendChild(suggestionCard);

        // 4. Display Encouragement
        const encouragementCard = createResultCard('encouragement', 'Encouragement', assistantResponse.encouragement);
        resultsPanel.appendChild(encouragementCard);

        // 5. Display Dual-Layer Verification Info
        if (data.dual_layer_verification) {
            const dualLayerCard = document.createElement('div');
            dualLayerCard.classList.add('result-card', 'dual-layer');
            dualLayerCard.innerHTML = `
                <h3>🔬 Dual-Layer Analysis</h3>
                <p><strong>Mathematical:</strong> ${data.dual_layer_verification.mathematical_analysis}</p>
                <p><strong>Grammatical:</strong> ${data.dual_layer_verification.grammatical_analysis}</p>
                <p><strong>Combined Confidence:</strong> ${Math.round(data.dual_layer_verification.combined_confidence * 100)}%</p>
            `;
            resultsPanel.appendChild(dualLayerCard);
        }

        // 6. Display Powered By Footer
        const footer = document.createElement('div');
        footer.classList.add('powered-by');
        const confidence = data.dual_layer_verification ? 
            data.dual_layer_verification.combined_confidence : 
            assistantResponse.confidence;
        footer.textContent = `${data.powered_by} (Confidence: ${Math.round(confidence * 100)}%)`;
        resultsPanel.appendChild(footer);
    }

    // --- Helper function to create result cards ---
    function createResultCard(type, title, content) {
        const card = document.createElement('div');
        card.classList.add('result-card', type);
        
        const cardTitle = document.createElement('h3');
        cardTitle.textContent = title;
        
        const cardContent = document.createElement('p');
        cardContent.textContent = content;

        card.appendChild(cardTitle);
        card.appendChild(cardContent);
        return card;
    }

    // --- Helper function to create grammar improvement cards ---
    function createGrammarCard(suggestions, grammarScore) {
        const card = document.createElement('div');
        card.classList.add('result-card', 'grammar');
        
        const cardTitle = document.createElement('h3');
        cardTitle.textContent = '📝 Grammar & Style Analysis';
        
        const scoreDiv = document.createElement('div');
        scoreDiv.innerHTML = `<strong>Grammar Score:</strong> ${Math.round(grammarScore * 100)}%`;
        
        const suggestionsList = document.createElement('ul');
        suggestions.forEach(suggestion => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>${suggestion.type}:</strong> "${suggestion.original}" → "${suggestion.suggested}" (${suggestion.explanation})`;
            suggestionsList.appendChild(li);
        });

        card.appendChild(cardTitle);
        card.appendChild(scoreDiv);
        card.appendChild(suggestionsList);
        return card;
    }
});
