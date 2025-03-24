export const HomeWebsiteStatus = {
    IN_PROGRESS: "in_progress",
    SERVING: "serving",
    EMPTY: "empty",
} as const;

export type HomeWebsiteStatusType =
    (typeof HomeWebsiteStatus)[keyof typeof HomeWebsiteStatus];
