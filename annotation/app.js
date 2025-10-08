class IssueAnnotationTool {
    constructor() {
        this.issues = [];
        this.annotations = [];
        this.labels = [];
        this.currentIssue = null;
        this.selectedLabels = new Set();
        this.applications = ['bookstack', 'indico', 'invoiceninja', 'prestashop'];
        
        // Workspace properties
        this.currentWorkspace = 'minh'; // Default workspace
        this.currentApplication = 'bookstack'; // Default application
        this.workspaces = [];
        this.workspaceStats = {};
        
        this.init();
    }

    async init() {
        await this.loadWorkspaces();
        this.setupEventListeners();
        await this.selectWorkspace('minh'); // Load default workspace
    }

    async loadWorkspaces() {
        try {
            const response = await fetch('/workspaces');
            const data = await response.json();
            this.workspaces = data.workspaces;
            this.workspaceStats = {};
            
            // Store stats for each workspace
            this.workspaces.forEach(workspace => {
                this.workspaceStats[workspace.name] = workspace.stats;
            });
        } catch (error) {
            console.error('Error loading workspaces:', error);
            alert('Error loading workspaces. Please check the server connection.');
        }
    }

    async loadWorkspaceData(workspace) {
        try {
            this.issues = [];
            this.annotations = [];
            this.labels = [];
            
            // Load issues from selected workspace
            for (const app of this.applications) {
                try {
                    const response = await fetch(`data/splits/${workspace}/${app}.json`);
                    const appIssues = await response.json();
                    this.issues.push(...appIssues.map(issue => ({ ...issue, application: app })));
                } catch (e) {
                    console.warn(`Could not load ${app} issues for workspace ${workspace}:`, e);
                }
            }

            // Load annotations from workspace
            try {
                const annotationsResponse = await fetch(`data/splits/${workspace}/annotations.json`);
                this.annotations = await annotationsResponse.json();
            } catch (e) {
                this.annotations = [];
            }

            // Load labels from workspace
            try {
                const labelsResponse = await fetch(`data/splits/${workspace}/labels.json`);
                this.labels = await labelsResponse.json();
            } catch (e) {
                // Try to copy from original if workspace doesn't have labels yet
                try {
                    const originalLabelsResponse = await fetch('data/original/labels.json');
                    this.labels = await originalLabelsResponse.json();
                    // Save to workspace for future use
                    await this.saveLabels();
                } catch (e2) {
                    this.labels = ['bug', 'feature', 'enhancement', 'documentation', 'performance', 'security', 'ui', 'api'];
                }
            }
        } catch (error) {
            console.error('Error loading workspace data:', error);
            alert('Error loading workspace data. Please check that all JSON files are present.');
        }
    }

    setupEventListeners() {
        // Workspace buttons
        this.setupWorkspaceButtons();
        
        // Application buttons
        this.setupApplicationButtons();

        // Search functionality
        const searchInput = document.getElementById('search-input');
        const clearSearch = document.getElementById('clear-search');
        
        if (searchInput) {
            searchInput.addEventListener('input', this.debounce(() => this.renderIssuesList(), 300));
        }
        if (clearSearch) {
            clearSearch.addEventListener('click', () => {
                searchInput.value = '';
                this.renderIssuesList();
            });
        }

        // Navigation
        const backToList = document.getElementById('back-to-list');
        if (backToList) {
            backToList.addEventListener('click', () => {
                this.showScreen('listing-screen');
            });
        }

        // Annotation panel
        const addLabelBtn = document.getElementById('add-label-btn');
        if (addLabelBtn) {
            addLabelBtn.addEventListener('click', () => this.addNewLabel());
        }
        
        const newLabelInput = document.getElementById('new-label-input');
        if (newLabelInput) {
            newLabelInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') this.addNewLabel();
            });
        }

        const saveAnnotation = document.getElementById('save-annotation');
        if (saveAnnotation) {
            saveAnnotation.addEventListener('click', () => this.saveAnnotation());
        }
        
        const clearSelection = document.getElementById('clear-selection');
        if (clearSelection) {
            clearSelection.addEventListener('click', () => this.clearLabelSelection());
        }
    }

    setupWorkspaceButtons() {
        document.querySelectorAll('.workspace-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectWorkspace(btn.dataset.workspace);
            });
        });
    }

    setupApplicationButtons() {
        document.querySelectorAll('.app-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectApplication(btn.dataset.app);
            });
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showScreen(screenId) {
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        document.getElementById(screenId).classList.add('active');
    }

    getFilteredIssues() {
        let filtered = [...this.issues];

        // Apply application filter (always filter by current app)
        filtered = filtered.filter(issue => issue.application === this.currentApplication);

        // Apply search filter
        const searchTerm = document.getElementById('search-input').value.toLowerCase();
        if (searchTerm) {
            filtered = filtered.filter(issue => 
                issue.title.toLowerCase().includes(searchTerm) ||
                issue.number.toString().includes(searchTerm)
            );
        }

        return filtered;
    }

    isAnnotated(issue) {
        return this.annotations.some(annotation => annotation.issue_id === issue.url);
    }

    getAnnotation(issue) {
        return this.annotations.find(annotation => annotation.issue_id === issue.url);
    }

    updateStats() {
        const total = this.issues.length;
        const annotated = this.annotations.length;
        const remaining = total - annotated;

        document.getElementById('total-issues').textContent = total;
        document.getElementById('annotated-issues').textContent = annotated;
        document.getElementById('remaining-issues').textContent = remaining;
    }

    renderIssuesList() {
        const container = document.getElementById('issues-container');
        const filteredIssues = this.getFilteredIssues();
        
        if (filteredIssues.length === 0) {
            container.innerHTML = '<div class="empty-state">No issues found matching your criteria.</div>';
            return;
        }

        const html = filteredIssues.map(issue => {
            const annotation = this.getAnnotation(issue);
            const isAnnotated = !!annotation;
            const preview = this.truncateText(issue.body || '', 100);
            
            // Escape HTML to prevent rendering issues
            const escapedTitle = this.escapeHtml(issue.title);
            const escapedPreview = this.escapeHtml(preview);
            const escapedUrl = this.escapeHtml(issue.url);
            
            return `
                <div class="issue-item ${isAnnotated ? 'annotated' : ''}" data-issue-url="${escapedUrl}">
                    <div class="issue-header">
                        <a href="#" class="issue-title" onclick="app.openAnnotation('${escapedUrl}'); return false;">
                            ${escapedTitle}
                        </a>
                        <div class="issue-meta">
                            #${issue.number} • ${issue.application} • ${new Date(issue.created_at).toLocaleDateString()}
                        </div>
                    </div>
                    ${escapedPreview ? `<div class="issue-preview">${escapedPreview}</div>` : ''}
                    ${isAnnotated && annotation.annotations.length > 0 ? `
                        <div class="issue-labels">
                            ${annotation.annotations.map(label => `<span class="label">${this.escapeHtml(label)}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        container.innerHTML = html;
    }

    truncateText(text, maxLength) {
        if (!text) return '';
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    openAnnotation(issueUrl) {
        const issue = this.issues.find(i => i.url === issueUrl);
        if (!issue) return;

        this.currentIssue = issue;
        this.selectedLabels.clear();
        
        // Load existing annotations if any
        const annotation = this.getAnnotation(issue);
        if (annotation) {
            annotation.annotations.forEach(label => this.selectedLabels.add(label));
        }

        this.renderAnnotationScreen();
        this.showScreen('annotation-screen');
    }

    renderAnnotationScreen() {
        if (!this.currentIssue) return;

        // Render issue details
        document.getElementById('issue-title').textContent = this.currentIssue.title;
        document.getElementById('issue-number').textContent = `#${this.currentIssue.number}`;
        document.getElementById('issue-state').textContent = this.currentIssue.state;
        document.getElementById('issue-date').textContent = new Date(this.currentIssue.created_at).toLocaleDateString();
        document.getElementById('issue-link').href = this.currentIssue.html_url;
        
        // Render issue body with basic markdown
        const bodyContent = this.renderMarkdown(this.currentIssue.body || '');
        document.getElementById('issue-body-content').innerHTML = bodyContent;

        // Render labels
        this.renderLabelsList();
        this.renderSelectedLabels();
    }

    renderMarkdown(text) {
        return text
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code>$1</code>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/^\n/, '<p>')
            .replace(/\n$/, '</p>')
            .replace(/\n/g, '<br>');
    }

    renderLabelsList() {
        const container = document.getElementById('labels-list');
        container.innerHTML = this.labels.map(label => {
            const isSelected = this.selectedLabels.has(label);
            return `
                <div class="label-item ${isSelected ? 'selected' : ''}" data-label="${label}">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} onchange="app.toggleLabel('${label}')">
                    <span>${label}</span>
                </div>
            `;
        }).join('');
    }

    renderSelectedLabels() {
        const container = document.getElementById('selected-labels');
        if (this.selectedLabels.size === 0) {
            container.innerHTML = '<div style="color: #656d76; font-size: 0.9rem;">No labels selected</div>';
            return;
        }

        container.innerHTML = Array.from(this.selectedLabels).map(label => `
            <div class="label-item">
                <span>${label}</span>
                <button onclick="app.removeSelectedLabel('${label}')" style="margin-left: auto; background: none; border: none; cursor: pointer;">×</button>
            </div>
        `).join('');
    }

    toggleLabel(label) {
        if (this.selectedLabels.has(label)) {
            this.selectedLabels.delete(label);
        } else {
            this.selectedLabels.add(label);
        }
        this.renderLabelsList();
        this.renderSelectedLabels();
    }

    removeSelectedLabel(label) {
        this.selectedLabels.delete(label);
        this.renderLabelsList();
        this.renderSelectedLabels();
    }

    addNewLabel() {
        const input = document.getElementById('new-label-input');
        const labelName = input.value.trim();
        
        if (!labelName) return;
        
        if (!this.labels.includes(labelName)) {
            this.labels.push(labelName);
            this.saveLabels();
        }
        
        this.selectedLabels.add(labelName);
        input.value = '';
        
        this.renderLabelsList();
        this.renderSelectedLabels();
    }

    clearLabelSelection() {
        this.selectedLabels.clear();
        this.renderLabelsList();
        this.renderSelectedLabels();
    }

    async saveAnnotation() {
        if (!this.currentIssue) return;

        const annotationData = {
            issue_id: this.currentIssue.url,
            annotations: Array.from(this.selectedLabels),
            annotated_at: new Date().toISOString()
        };

        // Remove existing annotation for this issue if any
        this.annotations = this.annotations.filter(a => a.issue_id !== this.currentIssue.url);
        
        // Add new annotation
        this.annotations.push(annotationData);

        try {
            await this.saveAnnotations();
            this.updateStats();
            this.showSaveStatus('Annotation saved!');
        } catch (error) {
            console.error('Error saving annotation:', error);
            this.showSaveStatus('Error saving annotation', true);
        }
    }

    async saveAnnotations() {
        try {
            const response = await fetch(`/save-annotations/${this.currentWorkspace}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.annotations)
            });
            
            const result = await response.json();
            if (result.success) {
                await this.updateWorkspaceMetadata();
                await this.loadWorkspaces(); // Refresh workspace stats
                this.updateWorkspaceButtons();
                this.updateApplicationButtons();
                this.updateStats();
                this.renderIssuesList();
                this.renderAnnotatedIssues();
                this.showSaveStatus('Annotations saved!');
            } else {
                throw new Error(result.error || 'Save failed');
            }
        } catch (error) {
            this.showSaveStatus('Error: ' + error.message, true);
        }
    }

    async saveLabels() {
        try {
            const response = await fetch(`/save-labels/${this.currentWorkspace}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.labels)
            });
            
            const result = await response.json();
            if (result.success) {
                this.showSaveStatus('Labels saved!');
            } else {
                throw new Error(result.error || 'Save failed');
            }
        } catch (error) {
            this.showSaveStatus('Error: ' + error.message, true);
        }
    }

    async updateWorkspaceMetadata() {
        try {
            const metadata = {
                last_activity: new Date().toISOString(),
                total_issues: this.issues.length,
                annotated_issues: this.annotations.length,
                progress_by_app: this.calculateProgressByApp()
            };
            
            await fetch(`/update-metadata/${this.currentWorkspace}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(metadata)
            });
        } catch (error) {
            console.warn('Failed to update workspace metadata:', error);
        }
    }

    calculateProgressByApp() {
        const progress = {};
        this.applications.forEach(app => {
            const appIssues = this.issues.filter(issue => issue.application === app);
            const appAnnotated = this.annotations.filter(annotation => {
                const issueUrl = annotation.issue_id;
                return issueUrl && issueUrl.includes(app);
            });
            progress[app] = {
                total: appIssues.length,
                annotated: appAnnotated.length
            };
        });
        return progress;
    }



    showSaveStatus(message, isError = false, duration = 3000) {
        const statusElement = document.getElementById('save-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.style.color = isError ? '#dc2626' : '#16a34a';
            statusElement.classList.add('visible');
            
            setTimeout(() => {
                statusElement.classList.remove('visible');
            }, duration);
        }
    }

    // Workspace and application management methods
    async selectWorkspace(workspace) {
        this.currentWorkspace = workspace;
        
        // Update active button state
        document.querySelectorAll('.workspace-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.workspace === workspace);
        });
        
        // Load workspace data
        await this.loadWorkspaceData(workspace);
        
        // Ensure we have a valid application selected
        if (!this.currentApplication || !this.applications.includes(this.currentApplication)) {
            this.currentApplication = 'bookstack';
        }
        
        // Update application button states
        document.querySelectorAll('.app-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.app === this.currentApplication);
        });
        
        // Update UI
        this.updateApplicationButtons();
        this.updateStats();
        this.renderIssuesList();
        this.renderAnnotatedIssues();
        
        this.showSaveStatus(`Switched to ${workspace}'s workspace`);
    }

    selectApplication(app) {
        this.currentApplication = app;
        
        // Update active button state
        document.querySelectorAll('.app-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.app === app);
        });
        
        // Re-render issues list
        this.renderIssuesList();
    }

    updateWorkspaceButtons() {
        this.workspaces.forEach(workspace => {
            const btn = document.querySelector(`[data-workspace="${workspace.name}"]`);
            if (btn) {
                const stats = workspace.stats;
                btn.querySelector('.annotated').textContent = stats.annotated_issues;
                btn.querySelector('.total').textContent = stats.total_issues;
            }
        });
    }

    updateApplicationButtons() {
        // Update counts for current workspace
        const appStats = this.calculateProgressByApp();
        
        // Update individual app buttons
        this.applications.forEach(app => {
            const btn = document.querySelector(`[data-app="${app}"]`);
            if (btn && appStats[app]) {
                btn.querySelector('.annotated').textContent = appStats[app].annotated;
                btn.querySelector('.total').textContent = appStats[app].total;
            }
        });
    }

    renderAnnotatedIssues() {
        const container = document.getElementById('annotated-list');
        const appStats = this.calculateProgressByApp();
        
        const annotatedHtml = Object.entries(appStats).map(([app, stats]) => {
            if (stats.annotated > 0) {
                return `
                    <div class="annotated-app">
                        <h4>${app.charAt(0).toUpperCase() + app.slice(1)}</h4>
                        <div class="annotated-count">${stats.annotated} annotated issues</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${(stats.annotated / stats.total * 100).toFixed(1)}%"></div>
                        </div>
                    </div>
                `;
            }
            return '';
        }).join('');
        
        if (annotatedHtml) {
            container.innerHTML = annotatedHtml;
        } else {
            container.innerHTML = '<div class="empty-state">No annotated issues yet.</div>';
        }
    }
}

// Initialize the application
const app = new IssueAnnotationTool();