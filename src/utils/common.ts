// Function to generate random IDs
export function generateId(type: 'test' | 'fixture' | 'environment'): string {
    // One time and deterministic for that type. To trace and link back later, esp. with FKs i.e. fixtures.
    const currentTime = Date.now().toString(36);
    return `${type}_${currentTime}_${Math.random().toString(36)}`;
}