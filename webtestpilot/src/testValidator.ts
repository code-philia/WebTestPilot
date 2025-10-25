import { TestItem } from './models';

export interface ValidationResult {
    isValid: boolean;
    errors: string[];
}

export class TestValidator {
    static validateTestFile(content: string): ValidationResult {
        const errors: string[] = [];
        
        try {
            const data = JSON.parse(content);
            
            // Check required fields
            if (!data.name || typeof data.name !== 'string') {
                errors.push('Test name is required and must be a string');
            }
            
            if (data.url && typeof data.url !== 'string') {
                errors.push('URL must be a string');
            }
            
            if (data.actions && !Array.isArray(data.actions)) {
                errors.push('Actions must be an array');
            } else if (data.actions) {
                data.actions.forEach((action: any, index: number) => {
                    if (!action.action || typeof action.action !== 'string') {
                        errors.push(`Action ${index + 1}: action description is required and must be a string`);
                    }
                    if (!action.expectedResult || typeof action.expectedResult !== 'string') {
                        errors.push(`Action ${index + 1}: expectedResult is required and must be a string`);
                    }
                });
            }
            
        } catch (error) {
            errors.push('Invalid JSON format');
        }
        
        return {
            isValid: errors.length === 0,
            errors
        };
    }
    
    static sanitizeTestItem(data: any): TestItem {
        return {
            id: data.id || '',
            name: data.name || 'Untitled Test',
            type: 'test',
            url: data.url || '',
            actions: data.actions || [],
            folderId: data.folderId,
            createdAt: data.createdAt ? new Date(data.createdAt) : new Date(),
            updatedAt: data.updatedAt ? new Date(data.updatedAt) : new Date()
        };
    }
}