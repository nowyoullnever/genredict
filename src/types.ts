export type Kind="genre"|"scene_movement"|"descriptor"|"meta";
export interface Node {id:string;name:string;slug:string;type:Kind;parents:string[];children:string[];depth:number|null;rymUrl:string|null;sourcePath:string[];aliases:string[];dateAdded:string|null;lastChanged:string|null}
export interface Edge {source:string;target:string;relation:"parent"}
export interface Graph {nodes:Node[];edges:Edge[]}
export interface Changes {generatedAt:string;addedNodes:string[];removedNodes:string[];addedEdges:Edge[];removedEdges:Edge[];typeChanges:{id:string;from:Kind;to:Kind}[]}