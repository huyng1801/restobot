import { useState, useCallback } from 'react';

export function useForm<T extends Record<string, any>>(
  initialState: T,
  validationSchema?: (values: T) => Record<string, string>
) {
  const [values, setValues] = useState<T>(initialState);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const setValue = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear error when user starts typing
    if (errors[name as string]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  }, [errors]);

  const setFieldTouched = useCallback((name: keyof T, isTouched: boolean = true) => {
    setTouched(prev => ({
      ...prev,
      [name]: isTouched
    }));
  }, []);

  const handleChange = useCallback((event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = event.target;
    
    let fieldValue: any = value;
    
    // Handle different input types
    if (type === 'checkbox') {
      fieldValue = (event.target as HTMLInputElement).checked;
    } else if (type === 'number') {
      fieldValue = value === '' ? '' : Number(value);
    }
    
    setValue(name as keyof T, fieldValue);
  }, [setValue]);

  const handleBlur = useCallback((event: React.FocusEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name } = event.target;
    setFieldTouched(name as keyof T);
  }, [setFieldTouched]);

  const validate = useCallback((): boolean => {
    if (!validationSchema) return true;
    
    const newErrors = validationSchema(values);
    setErrors(newErrors);
    
    // Mark all fields as touched to show errors
    const allTouched = Object.keys(values).reduce((acc, key) => ({
      ...acc,
      [key]: true
    }), {});
    setTouched(allTouched);
    
    return Object.keys(newErrors).length === 0;
  }, [values, validationSchema]);

  const reset = useCallback(() => {
    setValues(initialState);
    setErrors({});
    setTouched({});
  }, [initialState]);

  const setFormData = useCallback((newData: Partial<T>) => {
    setValues(prev => ({
      ...prev,
      ...newData
    }));
  }, []);

  return {
    values,
    errors,
    touched,
    setValue,
    setFieldTouched,
    handleChange,
    handleBlur,
    validate,
    reset,
    setFormData,
    isValid: Object.keys(errors).length === 0
  };
}