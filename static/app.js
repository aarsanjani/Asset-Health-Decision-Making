document.addEventListener('DOMContentLoaded', () => {
    const triggerBtn = document.getElementById('trigger-btn');
    const intentInput = document.getElementById('intent-input');
    const agentTeamList = document.getElementById('agent-team-list');
    const executionFeed = document.getElementById('execution-feed');
    const trajectoryPlot = document.getElementById('trajectory-plot');
    
    // Telemetry DOM elements
    const telVibration = document.getElementById('tel-vibration');
    const telTemp = document.getElementById('tel-temp');
    const telMw = document.getElementById('tel-mw');
    const telRedundancy = document.getElementById('tel-redundancy');
    
    // Governance DOM elements
    const governanceGateway = document.getElementById('governance-gateway');
    const recommendationSummary = document.getElementById('recommendation-summary');
    const approveBtn = document.getElementById('approve-btn');
    const rejectBtn = document.getElementById('reject-btn');
    
    // Modal DOM elements
    const successModal = document.getElementById('success-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    
    const activeAgentsCount = document.getElementById('active-agents-count');

    // Trigger simulation run
    triggerBtn.addEventListener('click', async () => {
        const intent = intentInput.value.trim();
        if (!intent) {
            alert('Please enter a valid operator intent.');
            return;
        }

        // 1. Loading State
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = '<span>🧠 Executing FCoT Reasoning Loops...</span>';
        
        executionFeed.innerHTML = `
            <div class="empty-feed-state">
                <div class="brain-icon" style="font-size: 64px;">⚡</div>
                <p>Root Overseer parsing intent & assembling agent team...</p>
            </div>
        `;
        agentTeamList.innerHTML = '<div class="empty-state">Assembling...</div>';
        governanceGateway.style.display = 'none';
        trajectoryPlot.innerHTML = '<div class="empty-state">Calculating...</div>';
        
        // Reset telemetry
        telVibration.innerText = '--';
        telTemp.innerText = '--';
        telMw.innerText = '--';
        telRedundancy.innerText = '--';
        activeAgentsCount.innerText = '0';

        try {
            // 2. Fetch from Backend
            const response = await fetch('/run-simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ intent: intent })
            });

            if (!response.ok) {
                throw new Error('Simulation endpoint failed.');
            }

            const data = await response.json();
            
            // 3. Render Dashboard State
            renderDashboard(data);

        } catch (error) {
            console.error(error);
            executionFeed.innerHTML = `
                <div class="empty-feed-state" style="color: var(--color-danger);">
                    <div class="brain-icon">⚠️</div>
                    <p>Error executing multi-agent system. Check console logs.</p>
                </div>
            `;
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = '<span>⚡ Trigger Autonomous Resolution</span>';
        }
    });

    // Render the complete dashboard with animation delays
    function renderDashboard(data) {
        // Reset button
        triggerBtn.disabled = false;
        triggerBtn.innerHTML = '<span>⚡ Trigger Autonomous Resolution</span>';

        // A. Assemble Agent Team
        const team = data.assembled_team;
        activeAgentsCount.innerText = team.length;
        agentTeamList.innerHTML = '';
        
        team.forEach(agentName => {
            const card = document.createElement('div');
            card.className = 'agent-card';
            
            let emoji = '🤖';
            let roleName = 'Specialist';
            if (agentName.includes('Vibration')) {
                emoji = '📳';
                roleName = 'Vibration Specialist Agent';
            } else if (agentName.includes('Supply Chain')) {
                emoji = '📦';
                roleName = 'Logistics Coordinator Agent';
            } else if (agentName.includes('DCS')) {
                emoji = '🎛️';
                roleName = 'DCS Control Specialist Agent';
            }
            
            card.innerHTML = `
                <div class="agent-avatar">${emoji}</div>
                <div class="agent-info">
                    <div class="agent-name">${agentName}</div>
                    <div class="agent-role">${roleName}</div>
                </div>
                <div class="agent-status-indicator"></div>
            `;
            agentTeamList.appendChild(card);
        });

        // B. Populate FCoT Feed Sequentially (Simulates Live Stream)
        executionFeed.innerHTML = '';
        const iterations = data.fcot_iterations;
        
        iterations.forEach((it, index) => {
            setTimeout(() => {
                const card = document.createElement('div');
                card.className = `fcot-card ${it.iteration === 3 ? 'recommended' : ''}`;
                
                const state = it.proposed_state;
                const metrics = it.metrics;
                
                card.innerHTML = `
                    <div class="fcot-header">
                        <div class="fcot-title">
                            <span>🔄 Iteration ${it.iteration}: ${it.phase}</span>
                        </div>
                        <span class="fcot-badge">${it.iteration === 3 ? '🏆 OPTIMUM' : 'REJECTED OPTIMUM'}</span>
                    </div>
                    <div class="fcot-content">
                        <div class="step-block thought">
                            <span class="block-label">Thought</span>
                            <p>${it.thought}</p>
                        </div>
                        <div class="step-block action">
                            <span class="block-label">Action</span>
                            <p>${it.action}</p>
                        </div>
                        <div class="step-block observation">
                            <span class="block-label">Observation / State Formulated</span>
                            <p><strong>Proposed State:</strong> ${state.description}</p>
                            <p style="margin-top: 8px; font-size: 13px; color: var(--text-muted); white-space: pre-line;">${it.observation}</p>
                        </div>
                        
                        <div class="fcot-metrics">
                            <div class="metric-bar-group">
                                <div class="metric-label-row">
                                    <span class="metric-label">OEE Score (f_max)</span>
                                    <span class="metric-value">${metrics.oee.toFixed(2)}</span>
                                </div>
                                <div class="metric-track">
                                    <div class="metric-fill oee" id="oee-fill-${it.iteration}"></div>
                                </div>
                            </div>
                            <div class="metric-bar-group">
                                <div class="metric-label-row">
                                    <span class="metric-label">Safety Risk (f_min)</span>
                                    <span class="metric-value">${metrics.risk.toFixed(2)}</span>
                                </div>
                                <div class="metric-track">
                                    <div class="metric-fill risk" id="risk-fill-${it.iteration}"></div>
                                </div>
                            </div>
                        </div>

                        <div class="reflection-box">
                            <span class="reflection-prompt">❓ FORCED REFLECTION: "What did you miss in this state regarding OEE and Risk?"</span>
                            <p class="reflection-body">"${it.reflection}"</p>
                        </div>
                    </div>
                `;
                executionFeed.appendChild(card);
                
                // Animate the metrics progress bars after rendering
                setTimeout(() => {
                    document.getElementById(`oee-fill-${it.iteration}`).style.width = `${metrics.oee * 100}%`;
                    document.getElementById(`risk-fill-${it.iteration}`).style.width = `${metrics.risk * 100}%`;
                }, 50);

                // Auto-scroll feed
                executionFeed.scrollTop = executionFeed.scrollHeight;

                // C. When reaching final iteration, show telemetry and governance
                if (index === iterations.length - 1) {
                    setTimeout(() => {
                        updateTelemetryAndGovernance(data);
                    }, 500);
                }

            }, index * 1200); // 1.2s delay per card
        });
    }

    // Update Telemetry & Bottom Governance Sign-Off Gateway
    function updateTelemetryAndGovernance(data) {
        const recState = data.recommended_state;
        
        // 1. Update Telemetry Grid Dials
        telVibration.innerText = '0.0';
        telVibration.style.color = 'var(--color-success)';
        
        telTemp.innerText = '25.0';
        telTemp.style.color = 'var(--color-success)';
        
        telMw.innerText = '500';
        telMw.style.color = 'var(--color-success)';
        
        telRedundancy.innerText = 'Pump 2B ACTIVE';
        telRedundancy.style.color = 'var(--color-success)';
        
        // 2. Render SVG Trajectory Graph (Hill Climbing Visualization)
        renderTrajectoryChart(data.fcot_iterations);

        // 3. Show Governance Panel
        recommendationSummary.innerHTML = `
            Deploy hot-swap to standby <strong>Pump 2B</strong> (98.5% health) over 30 minutes, 
            sustaining <strong>500 MW</strong> output, and isolate damaged <strong>Pump 2A</strong> for scheduled repair in 36 hours.
        `;
        governanceGateway.style.display = 'flex';
        governanceGateway.scrollIntoView({ behavior: 'smooth' });
    }

    // Render SVG Trajectory Chart
    function renderTrajectoryChart(iterations) {
        trajectoryPlot.innerHTML = '';
        
        // Width/height of the SVG container
        const width = 340;
        const height = 185;
        const padding = 30;

        // Scale functions
        const getX = (i) => padding + (i / 2) * (width - 2 * padding);
        const getY = (val) => height - padding - val * (height - 2 * padding);

        // Create points list
        const points = iterations.map((it, i) => {
            return {
                x: getX(i),
                oeeY: getY(it.metrics.oee),
                riskY: getY(it.metrics.risk),
                oeeVal: it.metrics.oee,
                riskVal: it.metrics.risk
            };
        });

        // Generate SVG
        let svgHtml = `
            <svg width="${width}" height="${height}" style="background: transparent;">
                <!-- Grid lines -->
                <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="var(--border-normal)" stroke-width="1"/>
                <line x1="${padding}" y1="${padding}" x2="${padding}" y2="${height - padding}" stroke="var(--border-normal)" stroke-width="1"/>
                
                <!-- Y Axis Labels -->
                <text x="${padding - 8}" y="${padding + 4}" fill="var(--text-muted)" font-size="10" text-anchor="end">1.0</text>
                <text x="${padding - 8}" y="${height - padding + 4}" fill="var(--text-muted)" font-size="10" text-anchor="end">0.0</text>
                
                <!-- X Axis Labels -->
                <text x="${points[0].x}" y="${height - padding + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">Iter 1</text>
                <text x="${points[1].x}" y="${height - padding + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">Iter 2</text>
                <text x="${points[2].x}" y="${height - padding + 18}" fill="var(--text-muted)" font-size="10" text-anchor="middle">Iter 3</text>

                <!-- OEE Path (Blue Curve) -->
                <path d="M ${points[0].x} ${points[0].oeeY} C ${points[0].x + 40} ${points[0].oeeY - 30}, ${points[1].x - 40} ${points[1].oeeY}, ${points[1].x} ${points[1].oeeY} C ${points[1].x + 40} ${points[1].oeeY - 50}, ${points[2].x - 40} ${points[2].oeeY}, ${points[2].x} ${points[2].oeeY}" 
                      fill="none" stroke="var(--color-primary)" stroke-width="3" stroke-linecap="round"/>

                <!-- Risk Path (Orange Curve) -->
                <path d="M ${points[0].x} ${points[0].riskY} C ${points[0].x + 40} ${points[0].riskY - 50}, ${points[1].x - 40} ${points[1].riskY}, ${points[1].x} ${points[1].riskY} C ${points[1].x + 40} ${points[1].riskY + 50}, ${points[2].x - 40} ${points[2].riskY}, ${points[2].x} ${points[2].riskY}" 
                      fill="none" stroke="var(--color-warning)" stroke-width="3" stroke-dasharray="4,4" stroke-linecap="round"/>
        `;

        // Add dots and values
        points.forEach((pt, i) => {
            svgHtml += `
                <!-- OEE Point -->
                <circle cx="${pt.x}" cy="${pt.oeeY}" r="5" fill="var(--color-primary)" filter="drop-shadow(0 0 6px var(--color-primary))"/>
                <text x="${pt.x}" y="${pt.oeeY - 8}" fill="var(--color-primary)" font-size="10" font-weight="bold" text-anchor="middle">${pt.oeeVal.toFixed(2)}</text>
                
                <!-- Risk Point -->
                <circle cx="${pt.x}" cy="${pt.riskY}" r="5" fill="var(--color-warning)" filter="drop-shadow(0 0 6px var(--color-warning))"/>
                <text x="${pt.x}" y="${pt.riskY + 16}" fill="var(--color-warning)" font-size="10" font-weight="bold" text-anchor="middle">${pt.riskVal.toFixed(2)}</text>
            `;
        });

        svgHtml += `
            </svg>
            <div style="position: absolute; bottom: 8px; display: flex; gap: 16px; font-size: 11px;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 10px; height: 10px; background: var(--color-primary); border-radius: 50%;"></div>
                    <span>OEE (f_max)</span>
                </div>
                <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 10px; height: 10px; background: var(--color-warning); border-radius: 50%;"></div>
                    <span>Safety Risk (f_min)</span>
                </div>
            </div>
        `;
        trajectoryPlot.innerHTML = svgHtml;
    }

    // Modal Events
    approveBtn.addEventListener('click', () => {
        successModal.style.display = 'flex';
    });

    rejectBtn.addEventListener('click', () => {
        governanceGateway.style.display = 'none';
        alert('Operational proposal rejected. Meta-Agent notified. Throttling and alternative routing will be re-calculated.');
    });

    closeModalBtn.addEventListener('click', () => {
        successModal.style.display = 'none';
        governanceGateway.style.display = 'none';
        executionFeed.innerHTML = `
            <div class="empty-feed-state" style="color: var(--color-success);">
                <div class="brain-icon">🛡️</div>
                <p>Hot-swap active. System state fully GOVERNED and operating at 100% capacity.</p>
            </div>
        `;
    });
});
