const DB_NAME = "anizenith_chat_history_db";
const STORE = "messages";
const VERSION = 1;

// Opens an IndexedDB database on the client's device.
// IndexedDB is a built-in browser storage system for storing structured data.
// Data stored here persists across page reloads and browser restarts until the user clears site data
function openDB() {
    return new Promise((resolve, reject) => {
        // Opens or creates a DB with the specific DB Name and Version
        const request = indexedDB.open(DB_NAME, VERSION);

        // Runs only when DB is created or version is upgraded
        request.onupgradeneeded = () => {
            const db = request.result;

            // Create object store
            if (!db.objectStoreNames.contains(STORE)) {
                const store = db.createObjectStore(STORE, {
                    keyPath: "id",        // primary key for each record
                    autoIncrement: true   // automatically generate IDs
                });
            }
        };

        // Fires when database connection is successfully opened
        request.onsuccess = () => resolve(request.result);

        // Fires if opening the database fails
        request.onerror = () => reject(request.error);
    });
}

// Fetches all messages stored in IndexedDB.
// Returns an array of message objects.
export async function pullMessages() {
    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, "readonly");
        const store = tx.objectStore(STORE);

        const req = store.getAll();

        req.onsuccess = () => resolve(req.result || []);
        req.onerror = () => reject(req.error);
    });
}


// Pushes a list of message objects to IndexedDB
// Overwrites full chat. Cheap operation since IndexedDB is small (chat logs)
export async function pushMessages(messages) {
    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction(STORE, "readwrite");
        const store = tx.objectStore(STORE);

        // Clear everything in database first
        const clearReq = store.clear();

        clearReq.onsuccess = () => {
            // Insert full messages state
            for (const msg of messages) {
                store.add(msg);
            }
            resolve(true);
        };

        clearReq.onerror = () => reject(clearReq.error);
    });
}