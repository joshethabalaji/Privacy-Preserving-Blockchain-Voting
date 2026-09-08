/**
 * Person 3 Frontend Application Logic
 * Interacts with Person 3 FastAPI backend, Ganache local blockchain, and audit hash chain.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Initial fetch
    refreshAll();

    // Attach Event Listeners
    document.getElementById("btnRefreshStatus").addEventListener("click", refreshAll);
    document.getElementById("btnStartElection").addEventListener("click", startElection);
    document.getElementById("btnEndElection").addEventListener("click", endElection);

    // Queue buttons
    document.getElementById("btnSeedQueue").addEventListener("click", seedQueue);
    document.getElementById("btnShuffleQueue").addEventListener("click", shuffleQueue);
    document.getElementById("btnProcessBatch").addEventListener("click", processBatch);
    document.getElementById("btnClearQueue").addEventListener("click", clearQueue);

    // Modal buttons
    document.getElementById("btnOpenAddModal").addEventListener("click", () => {
        document.getElementById("addBallotModal").style.display = "flex";
    });
    document.getElementById("btnCloseModal").addEventListener("click", () => {
        document.getElementById("addBallotModal").style.display = "none";
    });
    document.getElementById("btnCancelModal").addEventListener("click", () => {
        document.getElementById("addBallotModal").style.display = "none";
    });
    document.getElementById("btnSubmitModal").addEventListener("click", addCustomBallot);

    // Duplicate test
    document.getElementById("btnTestDuplicate").addEventListener("click", testDuplicateNullifier);

    // Audit buttons
    document.getElementById("btnVerifyAudit").addEventListener("click", verifyAudit);
    document.getElementById("btnRunTamperDemo").addEventListener("click", runTamperDemo);
});

async function refreshAll() {
    await fetchStatus();
    await fetchQueue();
    await fetchBlockchainRecords();
    await fetchAuditLog();
    await fetchTally();
    await fetchIntegrationLogs();
}

async function fetchStatus() {
    try {
        const res = await fetch("/api/election/status");
        const data = await res.json();

        const badge = document.getElementById("systemStatusBadge");
        const dot = badge.querySelector(".status-dot");
        const statusText = document.getElementById("ganacheStatusText");

        if (data.blockchain_connected) {
            dot.className = "status-dot connected";
            statusText.textContent = "Ganache Connected";
            document.getElementById("valGanacheState").textContent = "Active Local Node";
            document.getElementById("valGanacheState").style.color = "var(--accent-green)";
        } else {
            dot.className = "status-dot error";
            statusText.textContent = "Ganache Disconnected";
            document.getElementById("valGanacheState").textContent = "Disconnected";
            document.getElementById("valGanacheState").style.color = "var(--accent-red)";
        }

        document.getElementById("valContractAddress").textContent = data.contract_address || "Not Deployed";
        document.getElementById("valBlockNumber").textContent = data.block_number ?? "0";
        document.getElementById("valElectionState").textContent = data.status || "NOT_STARTED";
        document.getElementById("valElectionId").textContent = `ID: ${data.election_id || "None"}`;

        if (data.status === "ACTIVE") {
            document.getElementById("valElectionState").style.color = "var(--accent-green)";
        } else if (data.status === "ENDED") {
            document.getElementById("valElectionState").style.color = "var(--accent-red)";
        } else {
            document.getElementById("valElectionState").style.color = "var(--accent-amber)";
        }
    } catch (err) {
        console.error("Error fetching status:", err);
    }
}

async function startElection() {
    const electionId = document.getElementById("inputElectionId").value.trim() || "ELECTION_2026";
    try {
        const res = await fetch("/api/election/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ election_id: electionId }),
        });
        const data = await res.json();
        if (res.ok) {
            alert(`Election '${data.election_id}' started on blockchain! (Tx: ${data.transaction_hash.slice(0, 10)}...)`);
            refreshAll();
        } else {
            alert(`Failed: ${data.detail || "Error starting election"}`);
        }
    } catch (err) {
        alert("Error connecting to backend: " + err.message);
    }
}

async function endElection() {
    if (!confirm("Are you sure you want to end the active election on the smart contract?")) return;
    try {
        const res = await fetch("/api/election/end", { method: "POST" });
        const data = await res.json();
        if (res.ok) {
            alert("Election has ended on the blockchain.");
            refreshAll();
        } else {
            alert(`Failed: ${data.detail || "Error ending election"}`);
        }
    } catch (err) {
        alert("Error connecting to backend: " + err.message);
    }
}

async function fetchQueue() {
    try {
        const res = await fetch("/api/queue");
        const data = await res.json();
        const tbody = document.getElementById("queueTableBody");
        const badge = document.getElementById("queueCountBadge");

        badge.textContent = `${data.count} Queued`;

        if (!data.queue || data.queue.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="empty-cell">Queue is currently empty. Click "Seed 4 Test Ballots" above.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.queue.map((item, idx) => `
            <tr>
                <td><strong>${idx + 1}</strong></td>
                <td><span class="badge badge-outline">${item.election_id}</span></td>
                <td><code class="text-mono">${item.encrypted_ballot}</code></td>
                <td><code class="text-mono" style="color: var(--accent-blue);">${item.nullifier}</code></td>
                <td class="text-mono text-muted">${new Date(item.timestamp * 1000).toLocaleTimeString()}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error fetching queue:", err);
    }
}

async function seedQueue() {
    try {
        const res = await fetch("/api/integration/seed-dummy-queue", { method: "POST" });
        const data = await res.json();
        if (res.ok) {
            await fetchQueue();
            await fetchAuditLog();
        } else {
            alert(data.detail || "Error seeding queue");
        }
    } catch (err) {
        alert("Network error: " + err.message);
    }
}

async function shuffleQueue() {
    try {
        const res = await fetch("/api/queue/shuffle", { method: "POST" });
        const data = await res.json();
        if (res.ok) {
            await fetchQueue();
            await fetchAuditLog();
        } else {
            alert(data.detail || "Error shuffling queue");
        }
    } catch (err) {
        alert("Network error: " + err.message);
    }
}

async function processBatch() {
    try {
        const res = await fetch("/api/queue/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ max_batch_size: 10 }),
        });
        const data = await res.json();
        if (res.ok) {
            alert(`✓ ${data.message}\nTx Hash: ${data.transaction_hash}\nBlock Number: ${data.block_number}`);
            refreshAll();
        } else {
            alert(`✗ Submission Failed: ${data.detail || "Batch processing error"}`);
        }
    } catch (err) {
        alert("Network error: " + err.message);
    }
}

async function clearQueue() {
    try {
        await fetch("/api/queue", { method: "DELETE" });
        fetchQueue();
    } catch (err) {
        console.error("Error clearing queue:", err);
    }
}

async function addCustomBallot() {
    const electionId = document.getElementById("modalElectionId").value.trim();
    const encryptedBallot = document.getElementById("modalEncryptedBallot").value.trim();
    const nullifier = document.getElementById("modalNullifier").value.trim();

    if (!electionId || !encryptedBallot || !nullifier) {
        alert("All fields are required.");
        return;
    }

    try {
        const res = await fetch("/api/queue/add", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                election_id: electionId,
                encrypted_ballot: encryptedBallot,
                nullifier: nullifier,
            }),
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("addBallotModal").style.display = "none";
            refreshAll();
        } else {
            alert(`Error: ${data.detail}`);
        }
    } catch (err) {
        alert("Network error: " + err.message);
    }
}

async function fetchBlockchainRecords() {
    try {
        const res = await fetch("/api/blockchain/audit");
        const data = await res.json();
        const tbody = document.getElementById("blockchainTableBody");
        const badge = document.getElementById("onchainCountBadge");

        badge.textContent = `${data.total_votes_on_chain} Confirmed`;

        if (!data.records || data.records.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-cell">No votes recorded on blockchain yet.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.records.map(r => `
            <tr>
                <td><strong class="text-mono">${r.block_number}</strong></td>
                <td><span class="badge badge-outline">${r.batch_id}</span></td>
                <td><code class="text-mono" style="color: var(--accent-blue);">${r.nullifier}</code></td>
                <td><code class="text-mono">${r.encrypted_ballot}</code></td>
                <td class="text-mono text-muted">${new Date(r.timestamp * 1000).toLocaleString()}</td>
                <td><span class="badge badge-success">✓ Zero PII / Anonymous</span></td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error fetching blockchain records:", err);
    }
}

async function testDuplicateNullifier() {
    const nullifier = document.getElementById("inputTestNullifier").value.trim();
    const encryptedBallot = document.getElementById("inputTestBallot").value.trim();
    const electionId = document.getElementById("inputElectionId").value.trim() || "ELECTION_2026";
    const resultBox = document.getElementById("duplicateTestResult");

    resultBox.style.display = "block";
    resultBox.innerHTML = `<em>Submitting transaction to Ganache smart contract with nullifier: ${nullifier}...</em>`;
    resultBox.className = "test-result-box";

    try {
        const res = await fetch("/api/vote", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                election_id: electionId,
                encrypted_ballot: encryptedBallot,
                nullifier: nullifier,
                batch_id: "BATCH_TEST_REPLAY",
            }),
        });
        const data = await res.json();

        if (!res.ok) {
            resultBox.className = "test-result-box rejection-success";
            resultBox.innerHTML = `
                <strong>🛡️ REJECTION CONFIRMED BY SMART CONTRACT:</strong><br>
                Status Code: <code>${res.status}</code><br>
                Smart Contract Revert Message: <code>${data.detail}</code><br>
                <em>Double voting successfully blocked! The nullifier '${nullifier}' was already recorded in this election.</em>
            `;
            await fetchAuditLog();
        } else {
            resultBox.className = "test-result-box accepted";
            resultBox.innerHTML = `
                <strong>✓ NEW NULLIFIER ACCEPTED ON BLOCKCHAIN:</strong><br>
                Tx Hash: <code>${data.transaction_hash}</code><br>
                Block Number: <code>${data.block_number}</code><br>
                <em>Nullifier recorded on-chain for the first time.</em>
            `;
            refreshAll();
        }
    } catch (err) {
        resultBox.className = "test-result-box rejection-success";
        resultBox.innerHTML = `Network error: ${err.message}`;
    }
}

async function fetchAuditLog() {
    try {
        const res = await fetch("/api/audit");
        const data = await res.json();
        const tbody = document.getElementById("auditTableBody");

        if (!data.chain || data.chain.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="empty-cell">Audit chain empty.</td></tr>`;
            return;
        }

        tbody.innerHTML = data.chain.slice().reverse().map(entry => `
            <tr>
                <td><strong>#${entry.index}</strong></td>
                <td><span class="badge ${entry.event_type.includes('REJECT') ? 'badge-danger' : 'badge-info'}">${entry.event_type}</span></td>
                <td><span title="${entry.prev_hash}">${entry.prev_hash.slice(0, 10)}...</span></td>
                <td><span title="${entry.entry_hash}" style="color: var(--accent-purple);">${entry.entry_hash.slice(0, 10)}...</span></td>
                <td><code>${JSON.stringify(entry.event_data)}</code></td>
                <td class="text-muted">${entry.timestamp_iso || new Date(entry.timestamp * 1000).toLocaleTimeString()}</td>
            </tr>
        `).join("");
    } catch (err) {
        console.error("Error fetching audit log:", err);
    }
}

async function verifyAudit() {
    const banner = document.getElementById("auditVerifyBanner");
    banner.style.display = "block";
    banner.innerHTML = "<em>Recalculating SHA-256 links across entire audit chain...</em>";
    banner.className = "audit-verification-banner";

    try {
        const res = await fetch("/api/audit/verify");
        const data = await res.json();

        if (data.verified) {
            banner.className = "audit-verification-banner success";
            banner.innerHTML = `✓ ${data.message}`;
        } else {
            banner.className = "audit-verification-banner failed";
            banner.innerHTML = `✗ ${data.message}`;
        }
    } catch (err) {
        banner.className = "audit-verification-banner failed";
        banner.innerHTML = "Verification network error: " + err.message;
    }
}

async function runTamperDemo() {
    const outputGrid = document.getElementById("tamperOutputGrid");
    outputGrid.style.display = "grid";
    outputGrid.innerHTML = `<em>Running safe educational tamper simulation in memory...</em>`;

    try {
        const res = await fetch("/api/audit/tamper-demo", { method: "POST" });
        const data = await res.json();

        if (!data.success) {
            outputGrid.innerHTML = `<div class="empty-cell">${data.message}</div>`;
            return;
        }

        outputGrid.innerHTML = `
            <div class="tamper-box before">
                <h3>BEFORE (Original Hash Chain)</h3>
                <p>Entry #${data.before_tampering.entry_index} Original Payload:</p>
                <pre class="tamper-code">${JSON.stringify(data.before_tampering.event_data, null, 2)}</pre>
                <p class="badge badge-success">✓ Cryptographically Valid</p>
                <small>${data.before_tampering.verification.message}</small>
            </div>
            <div class="tamper-box after">
                <h3>AFTER (Attacker Injected Modification)</h3>
                <p>Entry #${data.after_tampering.entry_index} Altered Payload:</p>
                <pre class="tamper-code">${JSON.stringify(data.after_tampering.tampered_data, null, 2)}</pre>
                <p class="badge badge-danger">✗ Tampering Detected</p>
                <small style="color: var(--accent-red);">${data.after_tampering.verification.message}</small>
            </div>
        `;
    } catch (err) {
        outputGrid.innerHTML = `<div class="empty-cell">Tamper simulation error: ${err.message}</div>`;
    }
}

async function fetchTally() {
    try {
        const res = await fetch("/api/results");
        const data = await res.json();
        const container = document.getElementById("tallyContainer");

        if (!data.tally || Object.keys(data.tally).length === 0) {
            container.innerHTML = `<div class="empty-cell">No votes recorded yet. Submit a batch to see simulated distribution.</div>`;
            return;
        }

        let cardsHtml = '<div class="tally-grid">';
        for (const [candidate, count] of Object.entries(data.tally)) {
            cardsHtml += `
                <div class="tally-card">
                    <span class="tally-candidate-name">${candidate}</span>
                    <span class="tally-count">${count} <small style="font-size: 0.9rem; color: var(--text-muted);">votes</small></span>
                    <small class="text-dim">Simulated tally visualization</small>
                </div>
            `;
        }
        cardsHtml += '</div>';
        container.innerHTML = cardsHtml;
    } catch (err) {
        console.error("Error fetching tally:", err);
    }
}

async function fetchIntegrationLogs() {
    try {
        const res = await fetch("/api/integration/person1/notifications");
        const data = await res.json();
        const box = document.getElementById("integrationLogsBox");

        if (!data.dispatched_by_person3 || data.dispatched_by_person3.length === 0) {
            box.innerHTML = `<div class="empty-cell">No integration events dispatched yet. Submit a batch to trigger confirmation signals.</div>`;
            return;
        }

        box.innerHTML = data.dispatched_by_person3.map(n => `
            <div class="integration-entry">
                <div>
                    <strong>[Person 1 Notification]</strong> Status: <code>has_voted = TRUE</code> | Election: <code>${n.election_id}</code>
                </div>
                <div>
                    Tx: <code>${n.transaction_hash.slice(0, 10)}...</code> | Block: <code>${n.block_number}</code>
                </div>
            </div>
        `).join("");
    } catch (err) {
        console.error("Error fetching integration logs:", err);
    }
}
