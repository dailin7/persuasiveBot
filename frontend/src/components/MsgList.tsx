import * as React from 'react';
import { ListItemIcon, Divider, List, ListItem, ListItemButton, ListItemText } from '@mui/material';
import MarkUnreadChatAltIcon from '@mui/icons-material/MarkUnreadChatAlt';
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from "../app/store";
import { reload } from '../app/slices/misInformation';
import { useLazyGetMisinformationQuery } from '../app/slices/bot' 
import { useEffect } from 'react';


export default function MsgList() {
  const IDs:number[][] = useSelector((state:RootState) => state.messagesID.IDs)
  const dispatch = useDispatch()
  const [getMisInformation, result, lastPromiseInfo] = useLazyGetMisinformationQuery(); //TODO: start from here for CORS

  useEffect(() => {
    if (result.data) {
      dispatch(reload(result.data))
    }
  }, [result.fulfilledTimeStamp]);

  const updateMisinformation = (updatedId:number[]) => {
    getMisInformation(updatedId)
  }

  return (
    <React.Fragment>
      <List component="nav" disablePadding>
      {IDs?.map((id:number[]) => (
        <React.Fragment>
          <ListItem disablePadding>
            <ListItemButton  
              onClick={() => {updateMisinformation(id)}}
              disabled={result.isFetching || result.isLoading}
              >
              <ListItemIcon>
                <MarkUnreadChatAltIcon/>
              </ListItemIcon>
              <ListItemText 
                primary={`ConID: ${id[0]}, MsgID: ${id[1]}`}
                style={{
                  overflow: 'auto', 
                  whiteSpace: 'nowrap',
                }}>
              </ListItemText>
            </ListItemButton>
          </ListItem>
          <Divider></Divider> 
        </React.Fragment>
      ))}
        
      </List>
    </React.Fragment>
  );
}
