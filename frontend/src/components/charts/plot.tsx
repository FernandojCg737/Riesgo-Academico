"use client";

import dynamic from "next/dynamic";

export const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });
