export const fdaTools = {
  searchValidatedSymptoms: {
    description: "Search FDA validated symptoms for a vaccine",
    parameters: {
      vaccine: { type: "string" },
      symptoms: { type: "array", items: { type: "string" } }
    }
  },
  getControlledTrialData: {
    description: "Get controlled trial text for deeper analysis",
    parameters: {
      vaccine: { type: "string" },
      indication: { type: "string" }
    }
  }
} as const;

export type ToolName = keyof typeof fdaTools;
export type ToolParams<T extends ToolName> = {
  [K in keyof typeof fdaTools[T]["parameters"]]: any;
};
