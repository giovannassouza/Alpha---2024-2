import React, { useState } from "react";
import {
  Drawer,
  IconButton,
  List,
  ListItem,
  Tooltip,
  Avatar,
  Typography,
} from "@mui/material";
import { useNavigate } from "react-router-dom";

interface SideMenuProps {
  profileImage: string;
  categories: {
    icon: React.ReactNode;
    label: string;
    path: string;
  }[];
  onProfileClick: () => void;
}

const SideMenu: React.FC<SideMenuProps> = ({
  profileImage,
  categories,
  onProfileClick,
}) => {
  const [expanded, setExpanded] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleMouseEnter = () => setExpanded(true);
  const handleMouseLeave = () => setExpanded(false);

  return (
    <Drawer
      variant="permanent"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={`side-menu ${expanded ? "expanded" : "collapsed"}`}
      sx={{
        width: expanded ? 240 : 140,
        height: 900,
        transition: "width 0.3s ease",
        overflowX: "hidden",
        "& .MuiDrawer-paper": {
          width: expanded ? 240 : 140,
          boxSizing: "border-box",
        },
      }}
    >
      <div className="profile" onClick={onProfileClick}>
        <Avatar
          src={profileImage}
          alt="User Profile"
          sx={{ cursor: "pointer", margin: "16px auto" }}
        />
      </div>
      <List
        className="menu-items"
        sx={{ display: "flex", flexDirection: "column", gap: "24px" }}
      >
        {categories.map((category, index) => (
          <Tooltip
            key={index}
            title={expanded ? "" : category.label}
            placement="right"
          >
            <ListItem
              className="menu-item"
              onClick={() => navigate(category.path)}
              component="li"
              sx={{
                display: "flex",
                alignItems: "center",
                gap: "16px",
                color: "#333",
              }}
            >
              <IconButton>{category.icon}</IconButton>
              {expanded && (
                <Typography variant="body2" className="menu-text">
                  {category.label}
                </Typography>
              )}
              {!expanded && null}{" "}
              {/* Adiciona um elemento vazio quando expanded é false */}
            </ListItem>
          </Tooltip>
        ))}
      </List>
    </Drawer>
  );
};

export default SideMenu;
