import React from 'react';

const VideoStream = () => {
    return (
        <div>
            <img 
                src="http://127.0.0.1:5000/getFeed" 
                alt="Live Video Stream"
                style={{ width: "1110px" }}  // Adjust the width as needed
            />
        </div>
    );
};

export default VideoStream;