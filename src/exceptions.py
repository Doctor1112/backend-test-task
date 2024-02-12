from fastapi import HTTPException, status


ShiftTaskNotFoundException = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="shift task with this id does not exist")