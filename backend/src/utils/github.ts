
export const isValidGitHubUrl = (url: string): boolean => {
    try {
        const parsed = new URL(url);

        if(parsed.hostname !== 'github.com') {
            return false;
        }

        const parts = parsed.pathname.split('/').filter(Boolean);

        return parts.length >= 2;
    } catch {
        return false;
    }
}