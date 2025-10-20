// ==UserScript==
// @name         Amazon Teams Members Email Exporter
// @namespace    http://tampermonkey.net/
// @version      2.1
// @description  Extracts team member emails from visible table using pagination
// @author       Cedric, Q, & fieldinn
// @match        https://permissions.amazon.com/a/team/*
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Simple function to extract emails from HTML content
    function extractEmailsFromHTML(html) {
        const emails = [];

        // Match emails in format: (email@amazon.com) or email@amazon.com
        const emailMatches = html.match(/([a-zA-Z0-9._-]+@amazon\.com)/g);
        if (emailMatches) {
            emailMatches.forEach(email => {
                const cleanEmail = email.toLowerCase().trim();
                if (!emails.includes(cleanEmail)) {
                    emails.push(cleanEmail);
                }
            });
        }

        return emails;
    }

    // Get emails from currently visible table rows
    function getVisibleTableEmails() {
        const emails = [];
        const table = document.getElementById('datatable_dom_team_membership');

        if (table) {
            const rows = table.querySelectorAll('tbody tr');
            console.log(`Found ${rows.length} visible rows`);

            rows.forEach(row => {
                const nameCell = row.querySelector('td:first-child');
                if (nameCell && nameCell.innerHTML) {
                    const rowEmails = extractEmailsFromHTML(nameCell.innerHTML);
                    emails.push(...rowEmails);
                }
            });
        }

        return [...new Set(emails)]; // Remove duplicates
    }

    // Get all team members by navigating through DataTable pages
    async function getAllTeamMembersViaPagination() {
        const allEmails = [];

        if (typeof datatable_instance_team_membership === 'undefined') {
            throw new Error('Team membership table not found');
        }

        try {
            // First, try to set a larger page size to get more results per page
            const settings = datatable_instance_team_membership.fnSettings();
            const currentPageSize = settings._iDisplayLength || 10;

            console.log(`Current page size: ${currentPageSize}`);

            // Try to increase page size if possible
            if (typeof datatable_instance_team_membership.fnLengthChange === 'function') {
                datatable_instance_team_membership.fnLengthChange(100);
                console.log('Set page size to 100');
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for reload
            }

            // Get emails from first page
            let pageEmails = getVisibleTableEmails();
            allEmails.push(...pageEmails);
            console.log(`Page 1: Found ${pageEmails.length} emails`);

            // Check if there are more pages
            const pageInfo = datatable_instance_team_membership.fnPagingInfo();
            console.log('Paging info:', pageInfo);

            if (pageInfo && pageInfo.iTotalPages > 1) {
                console.log(`Navigating through ${pageInfo.iTotalPages} pages...`);

                // Go through remaining pages
                for (let page = 1; page < pageInfo.iTotalPages; page++) {
                    console.log(`Loading page ${page + 1}...`);

                    // Navigate to page
                    datatable_instance_team_membership.fnPageChange('next');

                    // Wait for page to load
                    await new Promise(resolve => setTimeout(resolve, 1500));

                    // Get emails from this page
                    pageEmails = getVisibleTableEmails();
                    allEmails.push(...pageEmails);
                    console.log(`Page ${page + 1}: Found ${pageEmails.length} emails`);
                }

                // Go back to first page
                datatable_instance_team_membership.fnPageChange('first');
            }

        } catch (error) {
            console.warn('Pagination navigation failed:', error);
            // Fallback: just get current visible emails
            const fallbackEmails = getVisibleTableEmails();
            allEmails.push(...fallbackEmails);
            console.log(`Fallback: Found ${fallbackEmails.length} emails from visible table`);
        }

        // Remove duplicates and return
        const uniqueEmails = [...new Set(allEmails)];
        console.log(`Total unique emails found: ${uniqueEmails.length}`);
        return uniqueEmails;
    }

    // Copy text to clipboard with fallback
    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(
                () => showNotification(`Copied ${text.split(', ').length} member emails to clipboard!`),
                (err) => {
                    console.warn('Clipboard API failed:', err);
                    fallbackCopy(text);
                }
            );
        } else {
            fallbackCopy(text);
        }
    }

    // Fallback copy method
    function fallbackCopy(text) {
        try {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.opacity = '0';

            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            const successful = document.execCommand('copy');
            document.body.removeChild(textArea);

            if (successful) {
                showNotification(`Copied ${text.split(', ').length} member emails to clipboard!`);
            } else {
                showManualCopyModal(text);
            }
        } catch (err) {
            console.error('Fallback copy failed:', err);
            showManualCopyModal(text);
        }
    }

    // Show manual copy modal
    function showManualCopyModal(text) {
        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 10001; display: flex;
            justify-content: center; align-items: center;
        `;

        const content = document.createElement('div');
        content.style.cssText = `
            background: white; padding: 20px; border-radius: 8px;
            max-width: 80%; max-height: 80%; overflow: auto;
        `;

        content.innerHTML = `
            <h3>Copy Emails Manually</h3>
            <p>Select all text below and copy manually (Ctrl+C):</p>
            <textarea readonly style="width: 100%; height: 200px; font-family: monospace;">${text}</textarea>
            <br><br>
            <button onclick="document.body.removeChild(this.closest('div').parentElement)" 
                    style="padding: 8px 16px; background: #007cba; color: white; border: none; border-radius: 4px;">
                Close
            </button>
        `;

        modal.appendChild(content);
        document.body.appendChild(modal);

        const textarea = content.querySelector('textarea');
        textarea.focus();
        textarea.select();

        showNotification('Clipboard access failed. Please copy manually.', 'error');
    }

    // Show notification
    function showNotification(message, type = 'success') {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; padding: 10px 20px;
            background: ${type === 'error' ? '#f44336' : '#4CAF50'}; color: white;
            border-radius: 4px; z-index: 10000; font-family: Arial, sans-serif;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 3000);
    }

    // Main function
    function main() {
        if (!window.location.href.includes('/a/team/')) {
            return;
        }

        // Create the copy button
        const copyButton = document.createElement('button');
        copyButton.textContent = 'Copy Team Member Emails';
        copyButton.style.cssText = `
            margin-left: 10px; padding: 5px 10px; background-color: #007cba;
            color: white; border: none; border-radius: 3px; cursor: pointer; font-size: 12px;
        `;

        copyButton.addEventListener('click', async () => {
            const originalText = copyButton.textContent;
            copyButton.textContent = 'Loading...';
            copyButton.disabled = true;

            try {
                const emails = await getAllTeamMembersViaPagination();

                if (emails.length > 0) {
                    const emailsCSV = emails.sort().join(', ');
                    console.log(`Final result: ${emails.length} unique member emails`);
                    console.log('Sample emails:', emails.slice(0, 5));
                    copyToClipboard(emailsCSV);
                } else {
                    showNotification('No member emails found', 'error');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Error extracting emails: ' + error.message, 'error');
            }

            copyButton.textContent = originalText;
            copyButton.disabled = false;
        });

        // Add button to page
        const headerElement = document.getElementById('header');
        if (headerElement) {
            headerElement.appendChild(copyButton);
        } else {
            document.body.appendChild(copyButton);
        }
    }

    // Wait for DataTables to be initialized
    function waitForDataTables() {
        if (typeof jQuery !== 'undefined' && typeof datatable_instance_team_membership !== 'undefined') {
            console.log('Team membership DataTable found');
            main();
        } else {
            setTimeout(waitForDataTables, 1000);
        }
    }

    // Start the script
    setTimeout(waitForDataTables, 2000);
})();