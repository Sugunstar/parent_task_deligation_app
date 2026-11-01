/**
 * LevelUp PWA - Global JavaScript
 */

// Escape HTML utility to prevent XSS in dynamic renders
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    return String(text)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Register PWA Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(reg => {
                console.log('[PWA] Service Worker registered:', reg.scope);
            })
            .catch(err => {
                console.warn('[PWA] Service Worker registration failed:', err);
            });
    });
}

// Request Notification Permission for alerts
async function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        try {
            await Notification.requestPermission();
        } catch (e) {
            console.warn('Could not request notification permission:', e);
        }
    }
}

// Check for emergency events periodically or show web notification
async function checkActiveEmergencies() {
    try {
        const res = await fetch('/api/emergency/');
        if (!res.ok) return;
        const emergencies = await res.json();
        
        // Find any unacknowledged emergency
        const unacked = emergencies.filter(e => !e.acknowledged);
        if (unacked.length > 0) {
            const latest = unacked[0];
            // Show browser notification if permitted and supported
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification('🚨 EMERGENCY DETECTED', {
                    body: `${latest.child_name || 'Child'}: ${latest.trigger_reason}`,
                    icon: '/static/icons/icon-192.png',
                    tag: `emergency-${latest.id}`,
                    requireInteraction: true
                });
            }
            
            // If not already on emergency page, highlight or alert
            if (!window.location.pathname.startsWith('/emergency')) {
                let alertBanner = document.getElementById('global-emergency-banner');
                if (!alertBanner) {
                    alertBanner = document.createElement('div');
                    alertBanner.id = 'global-emergency-banner';
                    alertBanner.style.cssText = 'position:fixed;top:55px;left:0;right:0;background:#ef4444;color:white;padding:10px 16px;text-align:center;font-weight:bold;z-index:999;box-shadow:0 2px 8px rgba(0,0,0,0.3);';
                    document.body.prepend(alertBanner);
                }
                alertBanner.innerHTML = `🚨 EMERGENCY: ${escapeHtml(latest.child_name || 'Child')} needs help! <a href="/emergency/${latest.id}" style="color:white;text-decoration:underline;margin-left:8px;">View Alert →</a>`;
            }
        } else {
            const alertBanner = document.getElementById('global-emergency-banner');
            if (alertBanner) alertBanner.remove();
        }
    } catch (e) {
        // Silent fail on network check
    }
}

// Run notification permission request on first user touch/click
window.addEventListener('click', () => {
    requestNotificationPermission();
}, { once: true });

// Check emergencies every 10 seconds
setInterval(checkActiveEmergencies, 10000);
document.addEventListener('DOMContentLoaded', checkActiveEmergencies);
