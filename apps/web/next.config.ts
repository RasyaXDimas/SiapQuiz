import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone dibutuhkan Dockerfile stage runner (apps/web/Dockerfile)
  output: "standalone",
};

export default nextConfig;
