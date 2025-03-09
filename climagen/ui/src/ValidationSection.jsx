import React, { useState } from 'react';
import ValidationCard from './ValidationCard.jsx';

const ValidationSection = ({
  validationObj,
  onValidationChange,
  mcqMode,
  handleValidation,
  handleInvalidReason,
  otherReason,
  setOtherReason,
  selected,
  invalidReason,
}) => {
  return (
      <ValidationCard 
      validation={validationObj} 
      selected={selected} 
      isMC={mcqMode} 
      handleValidation={handleValidation}
      handleInvalidReason={handleInvalidReason}
      otherReason={otherReason}
      setOtherReason={setOtherReason}
      invalidReason={invalidReason}
      />
  );
};

export default ValidationSection;
