export interface ITranslations {
    labels: { [key: string]: string };
    images: { [key: string]: string };
    accounts?: {
        register?: {
            form?: {
                invalid?: string;
            };
            success?: string;
        };
    };
}
