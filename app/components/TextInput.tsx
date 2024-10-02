import React, { ForwardedRef, forwardRef, useEffect, useState } from 'react'

interface TextInputProps {
  id: string
  label: string
  type: string
  required?: boolean
  monetary?: boolean
  defaultValue?: string | number
  disabled?: boolean
}

const TextInput = forwardRef(
  (
    {
      id,
      label,
      type,
      required,
      monetary = false,
      defaultValue = '',
      disabled = false
    }: TextInputProps,
    ref: ForwardedRef<HTMLInputElement>
  ) => {
    const [value, setValue] = useState<string>(
      monetary && defaultValue ? `$${defaultValue}` : String(defaultValue)
    )

    useEffect(() => {
      // Set the initial value from defaultValue prop, if provided
      setValue(monetary && defaultValue ? `$${defaultValue}` : String(defaultValue))
    }, [defaultValue, monetary])

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      let inputValue = e.target.value

      if (monetary) {
        // Remove non-numeric characters except for decimal points
        const numericValue = inputValue.replace(/[^0-9.]/g, '')

        // Update the value with the dollar sign
        setValue(numericValue ? `$${numericValue}` : '')
      } else {
        setValue(inputValue)
      }
    }

    return (
      <div className='relative'>
        <input
          type={monetary ? 'text' : type} // Use 'text' for monetary fields to allow the $ sign
          id={id}
          ref={ref}
          disabled={disabled}
          className={`peer w-full px-4 pt-4 pb-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-transparent placeholder-transparent 
            ${disabled ? 'opacity-50 cursor-not-allowed bg-gray-100' : ''}`}
          placeholder={label}
          required={required}
          value={value}
          onChange={handleChange}
        />
        <label
          htmlFor={id}
          className={`absolute left-4 -top-2 bg-white px-1 text-gray-500 text-sm transition-all duration-200 peer-placeholder-shown:text-base peer-placeholder-shown:top-2 peer-placeholder-shown:left-4 peer-placeholder-shown:text-gray-500 peer-placeholder-shown:bg-transparent peer-focus:-top-3 peer-focus:left-4 peer-focus:text-sm peer-focus:text-blue-500 peer-focus:bg-white
            ${disabled ? 'text-gray-400' : ''}`}
        >
          {label}
        </label>
      </div>
    )
  }
)

TextInput.displayName = 'TextInput'

export default TextInput
