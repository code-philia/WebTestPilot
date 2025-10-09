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
        this.currentFilter = 'all'; // Default filter: all, annotated, todos
        this.workspaces = [];
        this.workspaceStats = {};
        
        this.init();
    }

    async init() {
        await this.loadWorkspaces();
        this.setupEventListeners();
        await this.selectWorkspace('minh'); // Load default workspace
        
        // Set up periodic stats refresh every 30 seconds
        setInterval(() => {
            if (!document.hidden) { // Only refresh when tab is visible
                this.refreshStats();
            }
        }, 30000);
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
        this.issues = [];
        this.annotations = [];
        this.labels = [];
        
        await this.loadIssues(workspace);
        await this.loadAnnotations(workspace);
        await this.loadLabels(workspace);
    }

    async loadIssues(workspace) {
        const loadPromises = this.applications.map(async (app) => {
            try {
                const response = await fetch(`data/splits/${workspace}/${app}.json`);
                const appIssues = await response.json();
                this.issues.push(...appIssues.map(issue => ({ ...issue, application: app })));
            } catch (e) {
                console.warn(`Could not load ${app} issues for workspace ${workspace}:`, e);
            }
        });
        
        await Promise.all(loadPromises);
    }

    async loadAnnotations(workspace) {
        try {
            const response = await fetch(`data/splits/${workspace}/annotations.json`);
            this.annotations = await response.json();
        } catch (e) {
            this.annotations = [];
        }
    }

    async loadLabels(workspace) {
        try {
            const response = await fetch(`data/splits/${workspace}/labels.json`);
            this.labels = await response.json();
        } catch (e) {
            await this.loadDefaultLabels(workspace);
        }
    }

    async loadDefaultLabels(workspace) {
        try {
            const response = await fetch('data/original/labels.json');
            this.labels = await response.json();
            await this.saveLabels();
        } catch (e) {
            this.labels = ['bug', 'feature', 'enhancement', 'documentation', 'performance', 'security', 'ui', 'api'];
        }
    }

    setupEventListeners() {
        // Workspace buttons
        this.setupWorkspaceButtons();
        
        // Application buttons
        this.setupApplicationButtons();
        
        // Filter buttons
        this.setupFilterButtons();

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
                // Clear annotation status when returning to list
                const statusElement = document.getElementById('annotation-save-status');
                if (statusElement) {
                    statusElement.classList.remove('visible');
                }
                this.showScreen('listing-screen');
            });
        }

        // Issue navigation
        const prevIssue = document.getElementById('prev-issue');
        const nextIssue = document.getElementById('next-issue');
        
        if (prevIssue) {
            prevIssue.addEventListener('click', () => this.navigateIssue('prev'));
        }
        
        if (nextIssue) {
            nextIssue.addEventListener('click', () => this.navigateIssue('next'));
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

        // Keyboard shortcuts for annotation screen
        document.addEventListener('keydown', (e) => this.handleKeyboardShortcuts(e));
    }

    handleKeyboardShortcuts(e) {
        if (!this.isAnnotationScreenActive()) return;
        
        const shortcuts = {
            'ArrowLeft': () => this.navigateIssue('prev'),
            'ArrowRight': () => this.navigateIssue('next'),
            's': () => this.saveAnnotation(),
            ' ': () => this.toggleFocusedLabel(e)
        };
        
        const isModifierKey = e.ctrlKey || e.metaKey;
        const isInputField = e.target.matches('input, textarea');
        
        if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
            if (!isInputField) {
                e.preventDefault();
                shortcuts[e.key]();
            }
        } else if (e.key === 's' && isModifierKey) {
            e.preventDefault();
            shortcuts[e.key]();
        } else if (e.key === ' ' && e.target.matches('.label-item')) {
            e.preventDefault();
            shortcuts[e.key]();
        }
    }

    isAnnotationScreenActive() {
        return document.getElementById('annotation-screen').classList.contains('active');
    }

    toggleFocusedLabel(e) {
        const label = e.target.dataset.label;
        if (label) {
            this.toggleLabel(label);
        }

        // GitHub preview toggle
        const toggleIframe = document.getElementById('toggle-iframe');
        if (toggleIframe) {
            toggleIframe.addEventListener('click', () => this.toggleGithubPreview());
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

    setupFilterButtons() {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectFilter(btn.dataset.filter);
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

    async selectFilter(filter) {
        this.currentFilter = filter;
        
        // Update button states
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.filter === filter);
        });
        
        // Refresh stats in real-time
        await this.refreshStats();
        this.renderIssuesList();
        
        // Update navigation buttons if on annotation screen
        if (this.currentIssue && document.getElementById('annotation-screen').classList.contains('active')) {
            this.updateNavigationButtons();
        }
    }

    getFilteredIssues() {
        let filtered = [...this.issues];

        // Apply application filter (always filter by current app)
        filtered = filtered.filter(issue => issue.application === this.currentApplication);

        // Apply annotation filter
        if (this.currentFilter === 'annotated') {
            filtered = filtered.filter(issue => this.isAnnotated(issue));
        } else if (this.currentFilter === 'todos') {
            filtered = filtered.filter(issue => !this.isAnnotated(issue));
        }

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
        const filteredIssues = this.getFilteredIssues();
        const total = filteredIssues.length;
        const annotated = filteredIssues.filter(issue => this.isAnnotated(issue)).length;
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
        
        // Show status if issue is already annotated
        if (annotation && annotation.annotations.length > 0) {
            const labelsCount = annotation.annotations.length;
            const labelsText = labelsCount === 1 ? 'label' : 'labels';
            this.showAnnotationSaveStatus(
                `📝 This issue already has ${labelsCount} ${labelsText}: ${annotation.annotations.join(', ')}`,
                false,
                3000
            );
        } else {
            // Clear any previous status messages
            const statusElement = document.getElementById('annotation-save-status');
            if (statusElement) {
                statusElement.classList.remove('visible');
            }
        }
        
        this.showScreen('annotation-screen');
    }

    async navigateIssue(direction, saveBeforeNavigate = false) {
        // Save current annotation if requested and there are selected labels
        if (saveBeforeNavigate && this.selectedLabels.size > 0) {
            try {
                await this.saveAnnotation();
            } catch (error) {
                console.error('Error saving before navigation:', error);
                // Continue navigation even if save fails
            }
        }
        
        const filteredIssues = this.getFilteredIssues();
        const currentIndex = filteredIssues.findIndex(issue => issue.url === this.currentIssue.url);
        
        let nextIndex;
        if (direction === 'prev') {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : -1;
        } else { // next
            nextIndex = currentIndex < filteredIssues.length - 1 ? currentIndex + 1 : -1;
        }
        
        if (nextIndex >= 0) {
            const nextIssue = filteredIssues[nextIndex];
            this.openAnnotation(nextIssue.url);
        }
    }

    updateNavigationButtons() {
        const filteredIssues = this.getFilteredIssues();
        const currentIndex = filteredIssues.findIndex(issue => issue.url === this.currentIssue.url);
        
        const prevButton = document.getElementById('prev-issue');
        const nextButton = document.getElementById('next-issue');
        const positionElement = document.getElementById('nav-position');
        
        if (prevButton) {
            prevButton.disabled = currentIndex <= 0;
        }
        
        if (nextButton) {
            nextButton.disabled = currentIndex >= filteredIssues.length - 1 || currentIndex === -1;
        }
        
        if (positionElement) {
            if (currentIndex >= 0 && filteredIssues.length > 0) {
                positionElement.textContent = `${currentIndex + 1} / ${filteredIssues.length}`;
            } else {
                positionElement.textContent = '0 / 0';
            }
        }
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

        // Setup GitHub preview iframe
        this.setupGithubPreview();

        // Render labels
        this.renderLabelsList();
        this.renderSelectedLabels();
        
        // Update navigation buttons
        this.updateNavigationButtons();
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
        container.innerHTML = this.labels.map((label, index) => {
            const isSelected = this.selectedLabels.has(label);
            return `
                <div class="label-item ${isSelected ? 'selected' : ''}" data-label="${label}" data-index="${index}" onclick="app.toggleLabel('${label}')" title="Click to ${isSelected ? 'deselect' : 'select'} this label" tabindex="0">
                    <input type="checkbox" ${isSelected ? 'checked' : ''} onclick="event.stopPropagation()">
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
            <div class="label-item" onclick="app.removeSelectedLabel('${label}')" title="Click to remove">
                <span>${label}</span>
                <button onclick="event.stopPropagation(); app.removeSelectedLabel('${label}')" style="margin-left: auto; background: none; border: none; cursor: pointer;">×</button>
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

    setupGithubPreview() {
        if (!this.currentIssue) return;
        
        const iframe = document.getElementById('github-iframe');
        const toggleButton = document.getElementById('toggle-iframe');
        const iframeContainer = document.getElementById('iframe-container');
        
        if (iframe && this.currentIssue.html_url) {
            // Set iframe src to GitHub issue URL
            iframe.src = this.currentIssue.html_url;
            
            // Reset toggle state
            iframeContainer.style.display = 'none';
            toggleButton.textContent = 'Show Preview';
            toggleButton.classList.remove('active');
        }
    }

    toggleGithubPreview() {
        const iframeContainer = document.getElementById('iframe-container');
        const toggleButton = document.getElementById('toggle-iframe');
        
        if (!iframeContainer || !toggleButton) return;
        
        const isVisible = iframeContainer.style.display !== 'none';
        
        if (isVisible) {
            iframeContainer.style.display = 'none';
            toggleButton.textContent = 'Show Preview';
            toggleButton.classList.remove('active');
        } else {
            iframeContainer.style.display = 'block';
            toggleButton.textContent = 'Hide Preview';
            toggleButton.classList.add('active');
        }
    }

    async saveAnnotation() {
        if (!this.currentIssue) return;

        const saveButton = document.getElementById('save-annotation');
        const originalText = saveButton.textContent;
        
        // Show immediate feedback that save is starting
        this.showAnnotationSaveStatus('Saving annotation...', false, 0);
        saveButton.textContent = 'Saving...';
        saveButton.disabled = true;

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
            await this.refreshStats();
            
            // Show detailed success message
            const labelsCount = Array.from(this.selectedLabels).length;
            const labelsText = labelsCount === 1 ? 'label' : 'labels';
            this.showAnnotationSaveStatus(
                `✅ Successfully saved ${labelsCount} ${labelsText} for issue #${this.currentIssue.number}!`,
                false,
                4000
            );
            
            // Also show brief message in main status
            this.showSaveStatus('Annotation saved successfully!');
            
            // Reset button after a short delay
            setTimeout(() => {
                saveButton.textContent = originalText;
                saveButton.disabled = false;
            }, 1000);
            
        } catch (error) {
            console.error('Error saving annotation:', error);
            this.showAnnotationSaveStatus('❌ Error saving annotation. Please try again.', true, 5000);
            this.showSaveStatus('Error saving annotation', true);
            
            // Reset button immediately on error
            saveButton.textContent = originalText;
            saveButton.disabled = false;
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
                await this.loadWorkspaces(); // Refresh workspace stats
                this.updateWorkspaceButtons();
                this.updateApplicationButtons();
                this.updateStats();
                this.renderIssuesList();
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



    calculateProgressByApp() {
        const progress = {};
        
        // Create URL to app mapping from loaded issues
        const urlToApp = {};
        this.issues.forEach(issue => {
            if (issue.url && issue.application) {
                urlToApp[issue.url] = issue.application;
            }
        });
        
        // Calculate stats per app
        this.applications.forEach(app => {
            const appIssues = this.issues.filter(issue => issue.application === app);
            const appAnnotated = this.annotations.filter(annotation => {
                const issueUrl = annotation.issue_id;
                return issueUrl && urlToApp[issueUrl] === app;
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

    showAnnotationSaveStatus(message, isError = false, duration = 3000) {
        const statusElement = document.getElementById('annotation-save-status');
        if (statusElement) {
            statusElement.textContent = message;
            statusElement.style.color = isError ? '#dc2626' : '#16a34a';
            statusElement.style.fontWeight = '500';
            
            // Toggle error class for styling
            if (isError) {
                statusElement.classList.add('error');
            } else {
                statusElement.classList.remove('error');
            }
            
            statusElement.classList.add('visible');
            
            // Only auto-hide if duration > 0
            if (duration > 0) {
                setTimeout(() => {
                    statusElement.classList.remove('visible');
                }, duration);
            }
        }
    }



    // Real-time stats refresh
    async refreshStats() {
        await this.loadWorkspaces();
        this.updateWorkspaceButtons();
        this.updateApplicationButtons();
        this.updateStats();
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
        
        // Refresh all stats in real-time
        await this.refreshStats();
        this.renderIssuesList();
        
        this.showSaveStatus(`Switched to ${workspace}'s workspace`);
    }

    async selectApplication(app) {
        this.currentApplication = app;
        
        // Reset filter to 'all' when switching applications
        this.selectFilter('all');
        
        // Update active button state
        document.querySelectorAll('.app-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.app === app);
        });
        
        // Refresh stats in real-time
        await this.refreshStats();
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
        // Get the current workspace stats from server data
        const currentWorkspaceData = this.workspaces.find(w => w.name === this.currentWorkspace);
        if (currentWorkspaceData && currentWorkspaceData.stats && currentWorkspaceData.stats.progress_by_app) {
            const appStats = currentWorkspaceData.stats.progress_by_app;
            
            // Update individual app buttons
            this.applications.forEach(app => {
                const btn = document.querySelector(`[data-app="${app}"]`);
                if (btn && appStats[app]) {
                    const annotatedEl = btn.querySelector('.annotated');
                    const totalEl = btn.querySelector('.total');
                    if (annotatedEl && totalEl) {
                        annotatedEl.textContent = appStats[app].annotated;
                        totalEl.textContent = appStats[app].total;
                    }
                }
            });
        }
    }


}

// Initialize the application
const app = new IssueAnnotationTool();