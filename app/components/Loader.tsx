import React from "react";

interface LoaderProps {
  enabled: boolean;
}

const Loader: React.FC<LoaderProps> = ({ enabled }) => {
  if (!enabled) return null;

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-gray-800 bg-opacity-75">
    <div className="relative">
      <div className="animate-spin rounded-full h-16 w-16 border-4 border-transparent border-t-white"></div>
    </div>
  </div>
  );
};

export default Loader;
