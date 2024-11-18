import React, { ChangeEvent } from "react";

interface PhoneInputProps {
  className?: string;
  value: string;
  placeholder: string;
  onChange: (value: string) => void;
}

export function PhoneInput({
  className,
  value,
  placeholder,
  onChange,
}: PhoneInputProps) {
  function formatPhoneNumber(e: ChangeEvent<HTMLInputElement>) {
    const input = e.target.value.replace(/\D/g, "");
    let formatted = "";

    if (input.length === 0) {
      formatted = "";
    } else if (input.length <= 3) {
      formatted = `(${input}`;
    } else if (input.length <= 6) {
      formatted = `(${input.slice(0, 3)}) ${input.slice(3)}`;
    } else if (input.length <= 10) {
      formatted = `(${input.slice(0, 3)}) ${input.slice(3, 6)}-${input.slice(
        6
      )}`;
    } else {
      formatted = `(${input.slice(0, 3)}) ${input.slice(3, 6)}-${input.slice(
        6,
        10
      )}`;
    }

    onChange(formatted);
  }

  return (
    <div className="w-full h-full inline-flex space-x-2">
      <div className="py-2 px-4 bg-[#161616] border-2 border-[#242424] text-white rounded-none pointer-events-none">
        🇺🇸 +1
      </div>
      <input
        type="tel"
        autoComplete="tel"
        className={`py-2 px-4 bg-[#161616] text-white rounded-none focus:outline-none focus:ring-2 focus:ring-[#303030] border-2 border-[#242424] ${className}`}
        value={value}
        placeholder={placeholder}
        onChange={formatPhoneNumber}
        maxLength={16}
      />
    </div>
  );
}
