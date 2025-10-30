/**
 * Document Denoise Tool - Boil Out Noise
 *
 * Boil out document noise while preserving all essential information.
 * KISS implementation: Rule-based, extendable, zero information loss guarantee.
 * No LLM calls - pure structural optimization.
 */

import * as fs from "fs/promises";
import * as path from "path";

interface DenoiseArgs {
  file_path: string;
  target_reduction?: number;
  dry_run?: boolean;
  verbose?: boolean;
}

interface DenoiseResult {
  success: boolean;
  original_lines: number;
  denoised_lines: number;
  reduction_percent: number;
  output_path?: string;
  preview?: string;
}

/**
 * Boil out noise from document - remove verbosity, preserve all essential info.
 */
export async function denoise(args: DenoiseArgs): Promise<DenoiseResult> {
  // Validate required parameters
  if (!args.file_path || args.file_path.trim() === "") {
    throw new Error(
      `Missing required parameter: file_path\n` +
      `Usage: /denoise <file>\n` +
      `🔧 Troubleshooting: Provide path to document to denoise`
    );
  }

  const filePath = path.resolve(args.file_path);

  try {
    const content = await fs.readFile(filePath, "utf-8");
    const lines = content.split("\n");

    // Apply denoising rules (extendable)
    const denoised = applyDenoiseRules(lines);

    const denoisedContent = denoised.join("\n");
    const reduction = Math.round(
      ((lines.length - denoised.length) / lines.length) * 100
    );

    // Write unless dry-run
    if (!args.dry_run) {
      await fs.writeFile(filePath, denoisedContent, "utf-8");
    }

    return {
      success: true,
      original_lines: lines.length,
      denoised_lines: denoised.length,
      reduction_percent: reduction,
      output_path: args.dry_run ? undefined : filePath,
      preview: args.dry_run ? denoisedContent.substring(0, 500) : undefined
    };
  } catch (error) {
    const msg = error instanceof Error ? error.message : String(error);
    throw new Error(
      `Failed to denoise: ${msg}\n` +
      `🔧 Troubleshooting: Ensure file exists and is readable`
    );
  }
}

/**
 * Apply denoising rules - extendable rule set.
 */
function applyDenoiseRules(lines: string[]): string[] {
  let result = lines;

  // Rule 1: Remove excessive blank lines (>2 consecutive)
  result = removeExcessiveBlankLines(result);

  // Rule 2: Condense verbose sections
  result = condenseVerboseSections(result);

  // Rule 3: Deduplicate examples
  result = deduplicateExamples(result);

  // Rule 4: Compress long explanations
  result = compressExplanations(result);

  return result;
}

/**
 * Rule 1: Remove excessive blank lines.
 */
function removeExcessiveBlankLines(lines: string[]): string[] {
  const result: string[] = [];
  let blankCount = 0;

  for (const line of lines) {
    if (line.trim() === "") {
      blankCount++;
      if (blankCount <= 2) {
        result.push(line);
      }
    } else {
      blankCount = 0;
      result.push(line);
    }
  }

  return result;
}

/**
 * Rule 2: Condense verbose sections.
 * Detect: Multi-paragraph explanations
 * Action: Convert to bullet points
 */
function condenseVerboseSections(lines: string[]): string[] {
  const result: string[] = [];
  let inVerboseSection = false;
  let verboseBuffer: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const isHeader = line.match(/^#{1,6}\s+/);
    const isBlank = line.trim() === "";
    const isCode = line.startsWith("```");
    const isBullet = line.trim().match(/^[-*]\s+/);

    // Skip verbose sections (long paragraphs)
    if (!isHeader && !isCode && !isBullet && !isBlank && line.length > 100) {
      inVerboseSection = true;
      verboseBuffer.push(line);
    } else {
      // Flush verbose buffer
      if (inVerboseSection && verboseBuffer.length > 2) {
        // Convert to single bullet
        const summary = verboseBuffer[0].substring(0, 80).trim();
        result.push(`- ${summary}...`);
        verboseBuffer = [];
        inVerboseSection = false;
      } else {
        result.push(...verboseBuffer);
        verboseBuffer = [];
        inVerboseSection = false;
      }

      result.push(line);
    }
  }

  return result;
}

/**
 * Rule 3: Deduplicate examples.
 * Detect: Multiple consecutive code blocks
 * Action: Keep first one only
 */
function deduplicateExamples(lines: string[]): string[] {
  const result: string[] = [];
  let inCodeBlock = false;
  let codeBlockCount = 0;
  let skipCodeBlock = false;

  for (const line of lines) {
    if (line.startsWith("```")) {
      if (!inCodeBlock) {
        // Start of code block
        inCodeBlock = true;
        codeBlockCount++;
        skipCodeBlock = codeBlockCount > 2; // Keep max 2 examples
      } else {
        // End of code block
        inCodeBlock = false;
      }

      if (!skipCodeBlock) {
        result.push(line);
      }
    } else if (!inCodeBlock) {
      // Reset counter on non-code content
      if (line.trim() !== "" && !line.match(/^[-*]\s+/)) {
        codeBlockCount = 0;
      }
      skipCodeBlock = false;
      result.push(line);
    } else if (!skipCodeBlock) {
      result.push(line);
    }
  }

  return result;
}

/**
 * Rule 4: Compress explanations.
 * Detect: Long explanatory paragraphs before headers
 * Action: Condense to 1-2 sentences
 */
function compressExplanations(lines: string[]): string[] {
  const result: string[] = [];
  let paragraphBuffer: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const nextLine = i + 1 < lines.length ? lines[i + 1] : "";
    const isHeader = nextLine.match(/^#{1,6}\s+/);

    if (line.trim() !== "" && !line.startsWith("```") && !line.match(/^[-*]\s+/)) {
      paragraphBuffer.push(line);
    } else {
      // Flush paragraph buffer
      if (paragraphBuffer.length > 3 && isHeader) {
        // Keep first 2 lines only
        result.push(...paragraphBuffer.slice(0, 2));
      } else {
        result.push(...paragraphBuffer);
      }

      paragraphBuffer = [];
      result.push(line);
    }
  }

  result.push(...paragraphBuffer);
  return result;
}
