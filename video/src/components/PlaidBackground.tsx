import React from "react";
import { AbsoluteFill } from "remotion";

interface PlaidBackgroundProps {
  color1?: string;
  color2?: string;
  color3?: string;
  cellSize?: number;
}

export const PlaidBackground: React.FC<PlaidBackgroundProps> = ({
  color1 = "#f0f4f8",
  color2 = "#d4e4f1",
  color3 = "#bdd4ea",
  cellSize = 80,
}) => {
  const half = cellSize / 2;

  return (
    <AbsoluteFill>
      {/* Base color */}
      <div style={{ width: "100%", height: "100%", background: color1 }} />

      {/* Horizontal stripes */}
      <AbsoluteFill
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent ${half - 2}px,
              ${color2}88 ${half - 2}px,
              ${color2}88 ${half + 2}px,
              transparent ${half + 2}px,
              transparent ${cellSize}px
            )
          `,
        }}
      />

      {/* Vertical stripes */}
      <AbsoluteFill
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent ${half - 2}px,
              ${color2}88 ${half - 2}px,
              ${color2}88 ${half + 2}px,
              transparent ${half + 2}px,
              transparent ${cellSize}px
            )
          `,
        }}
      />

      {/* Thicker horizontal bands */}
      <AbsoluteFill
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              0deg,
              transparent,
              transparent ${cellSize - 12}px,
              ${color3}55 ${cellSize - 12}px,
              ${color3}55 ${cellSize}px
            )
          `,
        }}
      />

      {/* Thicker vertical bands */}
      <AbsoluteFill
        style={{
          backgroundImage: `
            repeating-linear-gradient(
              90deg,
              transparent,
              transparent ${cellSize - 12}px,
              ${color3}55 ${cellSize - 12}px,
              ${color3}55 ${cellSize}px
            )
          `,
        }}
      />
    </AbsoluteFill>
  );
};
