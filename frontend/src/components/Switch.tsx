import * as React from 'react';
import { useState } from 'react';
import { Button } from '@mui/material';
import { useLazyStartBotQuery, useLazyEndBotQuery } from '../app/slices/bot' 

export default function Switch() {
  const [displayText, setDisplayText] = useState('Start');
  const [startBot, startBotResult, lastStartBotInfo] = useLazyStartBotQuery(); //TODO: start from here for CORS
  const [endBot, endBotResult, lastEndBotInfo] = useLazyEndBotQuery(); //TODO: start from here for CORS

  const handleClick = () => {
    if (displayText === 'Start') {
      setDisplayText('End')
      startBot()
    }
    else {
      setDisplayText('Start')
      endBot()
    }
  };

  return (
    <Button variant='contained' onClick={handleClick} disabled={true}>
      {displayText}
    </Button>
  );
};


